"""
智能客服核心服务 - 电商平台与AI算力交互
处理买家咨询，调用AI智能体，自动计费
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, AsyncGenerator
from decimal import Decimal

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.ai.gateway import get_ai_gateway
from app.services.ai_power.billing import BillingService
from app.services.knowledge_retrieval import KnowledgeRetrieval, KNOWLEDGE_PROMPT_TEMPLATE, build_knowledge_context
from app.services.intent_recognition import get_intent_recognizer, BuyerIntent
from app.services.sentiment_analysis import get_sentiment_analyzer
from app.models.conversation import Conversation, Message
from app.models.ai_power import AIAccount

logger = logging.getLogger(__name__)


class SmartCustomerService:
    """
    智能客服服务
    
    核心功能：
    1. 接收电商平台买家咨询
    2. 构建AI对话上下文
    3. 调用AI智能体生成回复
    4. 自动计算并扣除算力费用
    5. 记录对话和用量
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_gateway = get_ai_gateway()
        self.billing_service = BillingService()
        self.knowledge_retrieval = KnowledgeRetrieval(db)
        self.intent_recognizer = get_intent_recognizer()
        self.sentiment_analyzer = get_sentiment_analyzer()
    
    async def handle_buyer_message(
        self,
        shop_id: str,
        buyer_id: str,
        buyer_message: str,
        platform: str = "manual",  # manual/taobao/jd/pdd/douyin
        conversation_id: Optional[str] = None,
        product_info: Optional[Dict] = None,
        order_info: Optional[Dict] = None
    ) -> Dict:
        """
        处理买家咨询消息
        
        Args:
            shop_id: 商户ID
            buyer_id: 买家ID
            buyer_message: 买家消息内容
            platform: 平台来源
            conversation_id: 对话ID（如有）
            product_info: 商品信息
            order_info: 订单信息
            
        Returns:
            {
                "success": True/False,
                "reply": "AI回复内容",
                "conversation_id": "对话ID",
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "total_cost": 0.015
                },
                "balance_info": {
                    "available": 100.00,
                    "deducted": 0.015
                }
            }
        """
        try:
            # 1. 意图识别
            intent, intent_confidence = self.intent_recognizer.recognize(buyer_message)
            intent_desc = self.intent_recognizer.get_intent_description(intent)
            strategy = self.intent_recognizer.get_suggested_response_strategy(intent)
            
            # 2. 情感分析
            sentiment_result = self.sentiment_analyzer.analyze(buyer_message)
            
            logger.info(f"买家消息分析 - 意图: {intent_desc}({intent_confidence:.2f}), "
                       f"情感: {sentiment_result['sentiment']}, 紧急度: {sentiment_result['urgency_level']}")
            
            # 3. 获取或创建对话
            if conversation_id:
                conversation = self.db.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
            else:
                conversation = None
            
            if not conversation:
                conversation = Conversation(
                    shop_id=shop_id,
                    buyer_id=buyer_id,
                    platform=platform,
                    status='active'
                )
                self.db.add(conversation)
                self.db.flush()
                conversation_id = str(conversation.id)
            
            # 4. 保存买家消息（包含意图和情感）
            buyer_msg = Message(
                conversation_id=conversation.id,
                role='buyer',
                content=buyer_message,
                platform=platform,
                intent=intent.value,
                sentiment=sentiment_result['sentiment']
            )
            self.db.add(buyer_msg)
            
            # 5. 如果是投诉或非常负面，标记需要人工介入
            if sentiment_result['needs_attention'] or intent == BuyerIntent.COMPLAINT:
                conversation.needs_attention = True
                conversation.attention_reason = f"意图: {intent_desc}, 情感: {sentiment_result['sentiment']}"
            
            # 6. 知识库检索
            knowledge_items = await self.knowledge_retrieval.search(
                shop_id=shop_id,
                query=buyer_message,
                top_k=3
            )
            
            # 7. 构建AI对话上下文
            messages = await self._build_context(
                conversation_id=conversation_id,
                shop_id=shop_id,
                product_info=product_info,
                order_info=order_info,
                intent=intent,
                sentiment=sentiment_result,
                knowledge_items=knowledge_items
            )
            
            # 8. 添加当前买家消息
            messages.append({
                "role": "user",
                "content": buyer_message
            })
            
            # 5. 检查AI账户余额
            account_info = await self.billing_service.get_account_info(shop_id)
            if account_info['total_available'] <= 0:
                return {
                    "success": False,
                    "error": "AI算力余额不足，请联系商户充值",
                    "conversation_id": conversation_id,
                    "reply": "抱歉，客服系统暂时无法回复，请稍后再试或联系人工客服。"
                }
            
            # 6. 调用AI智能体
            # 获取商户配置的默认模型
            model_name = await self._get_shop_default_model(shop_id)
            
            start_time = datetime.utcnow()
            ai_response = await self.ai_gateway.chat_completion(
                shop_id=shop_id,
                model_name=model_name,
                messages=messages,
                temperature=0.7,
                stream=False,
                conversation_id=conversation_id,
                message_id=str(buyer_msg.id)
            )
            
            response_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # 7. 处理AI响应
            if not ai_response.get("success"):
                logger.error(f"AI调用失败: {ai_response.get('error')}")
                return {
                    "success": False,
                    "error": ai_response.get('error', 'AI服务异常'),
                    "conversation_id": conversation_id,
                    "reply": "抱歉，客服系统暂时无法回复，请稍后再试。"
                }
            
            # 8. 保存AI回复
            ai_reply = ai_response["data"]["choices"][0]["message"]["content"]
            ai_msg = Message(
                conversation_id=conversation.id,
                role='assistant',
                content=ai_reply,
                ai_model=model_name,
                input_tokens=ai_response["usage"]["input_tokens"],
                output_tokens=ai_response["usage"]["output_tokens"],
                cost=Decimal(str(ai_response["usage"]["total_cost"]))
            )
            self.db.add(ai_msg)
            
            # 9. 更新对话最后消息时间
            conversation.last_message_at = datetime.utcnow()
            
            self.db.commit()
            
            # 10. 返回结果
            return {
                "success": True,
                "reply": ai_reply,
                "conversation_id": conversation_id,
                "message_id": str(ai_msg.id),
                "analysis": {
                    "intent": intent.value,
                    "intent_desc": intent_desc,
                    "sentiment": sentiment_result['sentiment'],
                    "sentiment_score": sentiment_result['sentiment_score'],
                    "urgency_level": sentiment_result['urgency_level'],
                    "needs_attention": sentiment_result['needs_attention'],
                    "knowledge_used": len(knowledge_items) > 0
                },
                "usage": {
                    "input_tokens": ai_response["usage"]["input_tokens"],
                    "output_tokens": ai_response["usage"]["output_tokens"],
                    "total_cost": float(ai_response["usage"]["total_cost"])
                },
                "balance_info": {
                    "available": account_info['total_available'] - float(ai_response["usage"]["total_cost"]),
                    "deducted": float(ai_response["usage"]["total_cost"]),
                    "free_quota_used": ai_response["usage"].get("free_quota_used", 0)
                }
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"处理买家消息失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id,
                "reply": "抱歉，系统繁忙，请稍后再试。"
            }
    
    async def handle_buyer_message_stream(
        self,
        shop_id: str,
        buyer_id: str,
        buyer_message: str,
        platform: str = "manual",
        conversation_id: Optional[str] = None,
        product_info: Optional[Dict] = None,
        order_info: Optional[Dict] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式处理买家咨询消息（SSE流式输出）
        
        Yields:
            SSE格式的数据流
        """
        try:
            # 1. 获取或创建对话
            if conversation_id:
                conversation = self.db.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
            else:
                conversation = None
            
            if not conversation:
                conversation = Conversation(
                    shop_id=shop_id,
                    buyer_id=buyer_id,
                    platform=platform,
                    status='active'
                )
                self.db.add(conversation)
                self.db.flush()
                conversation_id = str(conversation.id)
            
            # 2. 保存买家消息
            buyer_msg = Message(
                conversation_id=conversation.id,
                role='buyer',
                content=buyer_message,
                platform=platform
            )
            self.db.add(buyer_msg)
            
            # 3. 构建上下文
            messages = await self._build_context(
                conversation_id=conversation_id,
                shop_id=shop_id,
                product_info=product_info,
                order_info=order_info
            )
            messages.append({
                "role": "user",
                "content": buyer_message
            })
            
            # 4. 检查余额
            account_info = await self.billing_service.get_account_info(shop_id)
            if account_info['total_available'] <= 0:
                yield f"data: {json.dumps({'type': 'error', 'content': 'AI算力余额不足'})}\n\n"
                return
            
            # 5. 流式调用AI
            model_name = await self._get_shop_default_model(shop_id)
            
            full_reply = ""
            async for chunk in self.ai_gateway.chat_completion_stream(
                shop_id=shop_id,
                model_name=model_name,
                messages=messages
            ):
                if chunk.get("type") == "content":
                    full_reply += chunk["content"]
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk['content']})}\n\n"
                elif chunk.get("type") == "usage":
                    # 流式输出结束，保存消息和用量
                    ai_msg = Message(
                        conversation_id=conversation.id,
                        role='assistant',
                        content=full_reply,
                        ai_model=model_name,
                        input_tokens=chunk["usage"]["input_tokens"],
                        output_tokens=chunk["usage"]["output_tokens"],
                        cost=Decimal(str(chunk["usage"]["total_cost"]))
                    )
                    self.db.add(ai_msg)
                    conversation.last_message_at = datetime.utcnow()
                    self.db.commit()
                    
                    yield f"data: {json.dumps({'type': 'done', 'usage': chunk['usage']})}\n\n"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"流式处理失败: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    async def _build_context(
        self,
        conversation_id: str,
        shop_id: str,
        product_info: Optional[Dict] = None,
        order_info: Optional[Dict] = None,
        intent: Optional[BuyerIntent] = None,
        sentiment: Optional[Dict] = None,
        knowledge_items: Optional[List[Dict]] = None
    ) -> List[Dict[str, str]]:
        """
        构建AI对话上下文
        
        包含：
        1. 系统提示词（商户配置）
        2. 意图和情感指导
        3. 知识库内容
        4. 商品信息（如有）
        5. 订单信息（如有）
        6. 历史对话（最近N条）
        """
        messages = []
        
        # 1. 系统提示词
        system_prompt = await self._get_shop_system_prompt(shop_id)
        
        # 2. 添加意图和情感指导
        guidance_parts = []
        
        if intent and sentiment:
            guidance_parts.append(f"【当前买家状态】")
            guidance_parts.append(f"- 意图：{self.intent_recognizer.get_intent_description(intent)}")
            guidance_parts.append(f"- 情感：{sentiment['sentiment']} (分数: {sentiment['sentiment_score']})")
            guidance_parts.append(f"- 紧急程度：{sentiment['urgency_level']}")
            guidance_parts.append(f"- 回复语气：{sentiment['suggested_tone']}")
            
            # 根据意图添加特定指导
            if intent == BuyerIntent.COMPLAINT:
                guidance_parts.append("\n⚠️ 这是投诉场景，请立即诚恳道歉，积极解决问题，必要时建议转人工客服。")
            elif intent == BuyerIntent.REFUND:
                guidance_parts.append("\n💡 买家想退款，请先了解原因，尝试挽留，如无法挽留则快速处理退款。")
            elif intent == BuyerIntent.URGENT_ORDER:
                guidance_parts.append("\n⏰ 买家催单，请理解焦急心情，给出明确的发货/送达时间。")
        
        if guidance_parts:
            system_prompt += "\n\n" + "\n".join(guidance_parts)
        
        # 3. 添加知识库内容
        if knowledge_items:
            knowledge_context = build_knowledge_context(knowledge_items)
            system_prompt += "\n\n" + KNOWLEDGE_PROMPT_TEMPLATE.format(context=knowledge_context)
        
        # 4. 添加上下文信息
        context_parts = []
        
        if product_info:
            context_parts.append(f"【当前咨询商品】\n商品名称：{product_info.get('name', '')}\n价格：¥{product_info.get('price', '')}\n规格：{product_info.get('spec', '')}")
        
        if order_info:
            context_parts.append(f"【关联订单】\n订单号：{order_info.get('order_no', '')}\n状态：{order_info.get('status', '')}\n金额：¥{order_info.get('amount', '')}")
        
        if context_parts:
            system_prompt += "\n\n" + "\n\n".join(context_parts)
        
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # 5. 添加历史对话（最近10条）
        history = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(10).all()
        
        for msg in reversed(history):
            role = "user" if msg.role == "buyer" else "assistant"
            messages.append({
                "role": role,
                "content": msg.content
            })
        
        return messages
    
    async def _get_shop_system_prompt(self, shop_id: str) -> str:
        """获取商户系统提示词"""
        # 从商户配置中获取，或使用默认
        default_prompt = """你是专业的电商客服助手，请用友好、专业的语气回答买家问题。

回复原则：
1. 语气亲切友好，使用表情符号增加亲和力
2. 回答简洁明了，突出重点
3. 对于不确定的问题，引导买家联系人工客服
4. 主动推荐相关商品和优惠活动
5. 处理售后问题时，先安抚买家情绪

注意事项：
- 不要编造商品信息
- 不要承诺无法兑现的服务
- 遇到投诉时保持冷静和专业"""
        
        # TODO: 从数据库读取商户自定义提示词
        return default_prompt
    
    async def _get_shop_default_model(self, shop_id: str) -> str:
        """获取商户默认AI模型"""
        # TODO: 从商户配置中读取
        return "kimi-k2.5"
    
    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """获取对话历史"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "ai_model": msg.ai_model,
                "cost": float(msg.cost) if msg.cost else 0,
                "created_at": msg.created_at.isoformat()
            }
            for msg in reversed(messages)
        ]
    
    async def transfer_to_human(
        self,
        conversation_id: str,
        reason: str = "买家要求转人工"
    ) -> bool:
        """转接人工客服"""
        try:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if conversation:
                conversation.status = 'handoff'
                conversation.handoff_reason = reason
                
                # 添加转接记录
                handoff_msg = Message(
                    conversation_id=conversation.id,
                    role='system',
                    content=f"[系统] 已转接人工客服，原因：{reason}"
                )
                self.db.add(handoff_msg)
                self.db.commit()
                
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"转接人工失败: {e}")
            return False


# 单例模式
_smart_service = None

def get_smart_customer_service(db: Session) -> SmartCustomerService:
    """获取智能客服服务实例"""
    global _smart_service
    if _smart_service is None:
        _smart_service = SmartCustomerService(db)
    return _smart_service
