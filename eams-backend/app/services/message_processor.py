"""
消息处理流程
处理接收到的消息，包括意图识别、知识库匹配、AI回复生成
"""

from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
import logging

from app.models.conversation import Conversation, Message
from app.models.knowledge import Knowledge
from app.models.user import Shop
from app.services.ai_service import ai_service
from app.websocket.chat import notify_new_message, notify_conversation_update

logger = logging.getLogger(__name__)


class MessageProcessor:
    """消息处理器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def process_incoming_message(
        self,
        shop_id: str,
        platform_type: str,
        platform_user_id: str,
        platform_user_name: str,
        content: str,
        platform_msg_id: Optional[str] = None
    ) -> Dict:
        """
        处理接收到的用户消息
        
        流程:
        1. 查找或创建会话
        2. 保存用户消息
        3. 意图识别
        4. 判断是否需要转人工
        5. 知识库匹配
        6. AI生成回复
        7. 保存AI回复
        8. 发送通知
        """
        try:
            # 1. 查找或创建会话
            conversation = await self._get_or_create_conversation(
                shop_id=shop_id,
                platform_type=platform_type,
                platform_user_id=platform_user_id,
                platform_user_name=platform_user_name
            )
            
            # 2. 保存用户消息
            user_message = Message(
                conversation_id=conversation.id,
                platform_msg_id=platform_msg_id,
                direction="in",
                msg_type="text",
                content=content,
                sender_type="user",
                status="delivered"
            )
            self.db.add(user_message)
            
            # 更新会话最后消息
            conversation.last_message_preview = content[:200]
            conversation.last_message_at = datetime.utcnow()
            conversation.unread_count += 1
            
            await self.db.commit()
            await self.db.refresh(user_message)
            
            # 3. 获取对话上下文
            context = await self._get_conversation_context(conversation.id)
            
            # 4. 意图识别
            intent_result = await ai_service.classify_intent(
                text=content,
                context=context
            )
            
            # 更新消息意图
            user_message.intent = intent_result["intent"]
            user_message.intent_confidence = intent_result["confidence"]
            await self.db.commit()
            
            # 5. 判断是否需要转人工
            handoff_check = await ai_service.should_handoff(
                text=content,
                intent=intent_result["intent"],
                context=context
            )
            
            if handoff_check["should_handoff"]:
                # 转人工处理
                await self._handle_handoff(
                    conversation=conversation,
                    reason=handoff_check["reason"],
                    user_message=user_message
                )
                return {
                    "status": "handoff",
                    "conversation_id": str(conversation.id),
                    "message_id": str(user_message.id),
                    "handoff_reason": handoff_check["reason"]
                }
            
            # 6. 知识库匹配
            knowledge_items = await self._search_knowledge(
                shop_id=shop_id,
                query=content,
                intent=intent_result["intent"]
            )
            
            # 7. 获取店铺信息
            shop = await self.db.get(Shop, shop_id)
            shop_info = {"name": shop.name} if shop else None
            
            # 8. AI生成回复
            reply_result = await ai_service.generate_reply(
                text=content,
                intent=intent_result["intent"],
                context=context,
                knowledge_items=knowledge_items,
                shop_info=shop_info
            )
            
            # 9. 保存AI回复
            ai_message = Message(
                conversation_id=conversation.id,
                direction="out",
                msg_type="text",
                content=reply_result["content"],
                sender_type="ai",
                reply_type="ai",
                status="sent"
            )
            self.db.add(ai_message)
            
            # 更新会话
            conversation.last_message_preview = reply_result["content"][:200]
            conversation.last_message_at = datetime.utcnow()
            conversation.ai_message_count += 1
            
            await self.db.commit()
            await self.db.refresh(ai_message)
            
            # 10. 发送WebSocket通知
            await notify_new_message(
                shop_id=shop_id,
                conversation_id=str(conversation.id),
                message={
                    "id": str(user_message.id),
                    "direction": "in",
                    "content": content,
                    "created_at": user_message.created_at.isoformat()
                }
            )
            
            await notify_new_message(
                shop_id=shop_id,
                conversation_id=str(conversation.id),
                message={
                    "id": str(ai_message.id),
                    "direction": "out",
                    "content": reply_result["content"],
                    "created_at": ai_message.created_at.isoformat(),
                    "sender_type": "ai"
                }
            )
            
            return {
                "status": "replied",
                "conversation_id": str(conversation.id),
                "user_message_id": str(user_message.id),
                "ai_message_id": str(ai_message.id),
                "intent": intent_result["intent"],
                "reply": reply_result["content"]
            }
        
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            await self.db.rollback()
            raise
    
    async def send_manual_reply(
        self,
        conversation_id: str,
        content: str,
        sender_id: str,
        sender_name: str
    ) -> Dict:
        """发送人工客服回复"""
        conversation = await self.db.get(Conversation, conversation_id)
        if not conversation:
            raise ValueError("会话不存在")
        
        message = Message(
            conversation_id=conversation.id,
            direction="out",
            msg_type="text",
            content=content,
            sender_type="agent",
            sender_id=sender_id,
            sender_name=sender_name,
            reply_type="manual",
            status="sent"
        )
        self.db.add(message)
        
        # 更新会话
        conversation.last_message_preview = content[:200]
        conversation.last_message_at = datetime.utcnow()
        conversation.manual_message_count += 1
        conversation.unread_count = 0  # 人工回复后重置未读
        
        await self.db.commit()
        await self.db.refresh(message)
        
        # 发送通知
        await notify_new_message(
            shop_id=str(conversation.shop_id),
            conversation_id=conversation_id,
            message={
                "id": str(message.id),
                "direction": "out",
                "content": content,
                "sender_name": sender_name,
                "created_at": message.created_at.isoformat()
            }
        )
        
        return {
            "id": str(message.id),
            "content": content,
            "created_at": message.created_at.isoformat()
        }
    
    async def mark_conversation_read(self, conversation_id: str, user_id: str):
        """标记会话已读"""
        conversation = await self.db.get(Conversation, conversation_id)
        if conversation:
            conversation.unread_count = 0
            await self.db.commit()
    
    async def _get_or_create_conversation(
        self,
        shop_id: str,
        platform_type: str,
        platform_user_id: str,
        platform_user_name: str
    ) -> Conversation:
        """查找或创建会话"""
        # 查找现有会话
        result = await self.db.execute(
            select(Conversation).where(
                and_(
                    Conversation.shop_id == shop_id,
                    Conversation.platform_type == platform_type,
                    Conversation.platform_user_id == platform_user_id,
                    Conversation.status == "active"
                )
            )
        )
        conversation = result.scalar_one_or_none()
        
        if conversation:
            return conversation
        
        # 创建新会话
        conversation = Conversation(
            shop_id=shop_id,
            platform_type=platform_type,
            platform_user_id=platform_user_id,
            platform_user_name=platform_user_name,
            status="active"
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        
        # 通知新会话
        await notify_conversation_update(
            shop_id=shop_id,
            conversation_id=str(conversation.id),
            update_type="new_conversation",
            data={
                "platform_user_name": platform_user_name,
                "platform_type": platform_type
            }
        )
        
        return conversation
    
    async def _get_conversation_context(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """获取对话上下文"""
        result = await self.db.execute(
            select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.desc()).limit(limit)
        )
        messages = result.scalars().all()
        
        return [
            {
                "direction": msg.direction,
                "content": msg.content,
                "sender_type": msg.sender_type
            }
            for msg in reversed(messages)
        ]
    
    async def _search_knowledge(
        self,
        shop_id: str,
        query: str,
        intent: str,
        limit: int = 3
    ) -> List[Dict]:
        """搜索知识库"""
        # 简单的关键词匹配（实际应该使用全文搜索）
        result = await self.db.execute(
            select(Knowledge).where(
                and_(
                    Knowledge.shop_id == shop_id,
                    Knowledge.status == "active"
                )
            ).limit(limit * 2)  # 多取一些用于后续排序
        )
        
        items = result.scalars().all()
        
        # 简单的相关性排序
        scored_items = []
        query_words = set(query.lower().split())
        
        for item in items:
            score = 0
            question_words = set(item.question.lower().split())
            
            # 关键词匹配
            if item.keywords:
                for kw in item.keywords:
                    if kw.lower() in query.lower():
                        score += 3
            
            # 问题文本匹配
            overlap = query_words & question_words
            score += len(overlap)
            
            # 意图匹配
            if intent in item.question.lower():
                score += 2
            
            scored_items.append((score, item))
        
        # 按分数排序
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        return [
            {
                "question": item.question,
                "answer": item.answer
            }
            for _, item in scored_items[:limit]
        ]
    
    async def _handle_handoff(
        self,
        conversation: Conversation,
        reason: str,
        user_message: Message
    ):
        """处理转人工"""
        from app.models.conversation import Handoff
        
        # 更新会话状态
        conversation.status = "pending_handoff"
        conversation.handoff_reason = reason
        
        # 创建转人工记录
        handoff = Handoff(
            conversation_id=conversation.id,
            shop_id=conversation.shop_id,
            reason=reason,
            triggered_by="ai",
            status="pending"
        )
        self.db.add(handoff)
        
        await self.db.commit()
        
        # 发送通知
        from app.websocket.chat import notify_handoff_request
        await notify_handoff_request(
            shop_id=str(conversation.shop_id),
            conversation_id=str(conversation.id),
            handoff_info={
                "reason": reason,
                "user_message": user_message.content,
                "platform_user_name": conversation.platform_user_name
            }
        )
