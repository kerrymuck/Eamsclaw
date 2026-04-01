"""
AI智能回复引擎
支持多模型、知识库RAG、上下文管理
"""

from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import json
import re
from datetime import datetime


class MessageIntent(Enum):
    """消息意图类型"""
    PRODUCT_INQUIRY = "product_inquiry"      # 商品咨询
    ORDER_INQUIRY = "order_inquiry"          # 订单查询
    LOGISTICS_INQUIRY = "logistics_inquiry"  # 物流查询
    AFTER_SALES = "after_sales"              # 售后问题
    COMPLAINT = "complaint"                  # 投诉
    GREETING = "greeting"                    # 问候
    PRICE_NEGOTIATION = "price_negotiation"  # 议价
    GENERAL = "general"                      # 一般咨询
    UNKNOWN = "unknown"                      # 未知


class ResponseType(Enum):
    """回复类型"""
    DIRECT = "direct"              # 直接回复
    NEED_CLARIFY = "need_clarify"  # 需要澄清
    NEED_HUMAN = "need_human"      # 需要人工
    FOLLOW_UP = "follow_up"        # 需要跟进


@dataclass
class CustomerContext:
    """客户上下文信息"""
    customer_id: str
    customer_name: str
    platform: str
    shop_id: str
    
    # 历史会话
    conversation_history: List[Dict[str, Any]] = None
    
    # 订单信息
    recent_orders: List[Dict[str, Any]] = None
    
    # 用户画像
    tags: List[str] = None
    vip_level: str = "normal"
    purchase_count: int = 0
    total_spent: float = 0.0
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.recent_orders is None:
            self.recent_orders = []
        if self.tags is None:
            self.tags = []


@dataclass
class AIResponse:
    """AI回复结果"""
    content: str
    response_type: ResponseType
    intent: MessageIntent
    confidence: float
    suggested_actions: List[Dict[str, Any]] = None
    knowledge_sources: List[str] = None
    need_human_review: bool = False
    
    def __post_init__(self):
        if self.suggested_actions is None:
            self.suggested_actions = []
        if self.knowledge_sources is None:
            self.knowledge_sources = []


class IntentClassifier:
    """意图分类器"""
    
    # 意图关键词映射
    INTENT_PATTERNS = {
        MessageIntent.PRODUCT_INQUIRY: [
            r".*?(价格|多少钱|怎么卖|有货吗|库存|尺寸|颜色|规格).*?",
            r".*?(介绍|详情|参数|材质|质量|怎么样|好用吗).*?",
            r".*?有没有.*?(货|款|型号|颜色|尺码).*?",
        ],
        MessageIntent.ORDER_INQUIRY: [
            r".*?(订单|下单|购买|付款|支付|取消|修改).*?",
            r".*?(查订单|我的订单|订单号|订单状态).*?",
            r".*?订单.*?(在哪|怎么样|如何|怎么).*?",
        ],
        MessageIntent.LOGISTICS_INQUIRY: [
            r".*?(物流|快递|发货|配送|送到|几天|多久|什么时候到).*?",
            r".*?(查物流|跟踪|轨迹|到哪了|派送).*?",
            r".*?(单号|运单|查询).*?",
        ],
        MessageIntent.AFTER_SALES: [
            r".*?(退货|退款|换货|售后|维修|保修).*?",
            r".*?(质量问题|坏了|不好用|不满意|想退).*?",
            r".*?(怎么退|如何退|退钱|赔偿).*?",
        ],
        MessageIntent.COMPLAINT: [
            r".*?(投诉|举报|差评|曝光|欺骗|骗子).*?",
            r".*?(服务态度|态度差|骂人|不理人).*?",
            r".*?(欺骗|虚假宣传|假货|伪劣).*?",
        ],
        MessageIntent.GREETING: [
            r"^(你好|您好|在吗|有人吗|客服|亲|hi|hello|在不在).*?$",
            r".*?(早上好|下午好|晚上好).*?",
        ],
        MessageIntent.PRICE_NEGOTIATION: [
            r".*?(便宜|优惠|折扣|降价|便宜点|能少吗).*?",
            r".*?(太贵|价格高|便宜些|打个折|优惠点).*?",
            r".*?(最低价|最低多少|还能少吗|包个邮).*?",
        ],
    }
    
    @classmethod
    def classify(cls, message: str) -> tuple[MessageIntent, float]:
        """
        分类消息意图
        
        Returns:
            (意图类型, 置信度)
        """
        message = message.lower().strip()
        
        for intent, patterns in cls.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, message, re.IGNORECASE):
                    # 计算置信度（简单实现）
                    confidence = 0.8 + 0.1 * len(patterns)
                    return intent, min(confidence, 0.95)
        
        return MessageIntent.UNKNOWN, 0.3


class KnowledgeBase:
    """知识库管理"""
    
    def __init__(self):
        self.faqs: Dict[str, Dict[str, Any]] = {}
        self.product_knowledge: Dict[str, Dict[str, Any]] = {}
        self.shop_policies: Dict[str, str] = {}
    
    async def search(self, query: str, shop_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        搜索知识库
        
        Args:
            query: 查询内容
            shop_id: 店铺ID
            limit: 返回数量限制
            
        Returns:
            相关知识条目列表
        """
        results = []
        
        # 简单关键词匹配（实际应使用向量检索）
        query_keywords = set(query.lower().split())
        
        # 搜索FAQ
        for faq_id, faq in self.faqs.items():
            if faq.get("shop_id") == shop_id or faq.get("is_global", False):
                faq_keywords = set(faq.get("keywords", []))
                score = len(query_keywords & faq_keywords) / len(query_keywords | faq_keywords) if query_keywords else 0
                if score > 0.3:
                    results.append({
                        "type": "faq",
                        "id": faq_id,
                        "question": faq["question"],
                        "answer": faq["answer"],
                        "score": score
                    })
        
        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    async def add_faq(self, shop_id: str, question: str, answer: str, keywords: List[str] = None):
        """添加FAQ"""
        faq_id = f"faq_{shop_id}_{len(self.faqs)}"
        self.faqs[faq_id] = {
            "shop_id": shop_id,
            "question": question,
            "answer": answer,
            "keywords": keywords or [],
            "created_at": datetime.now().isoformat()
        }
        return faq_id


class AIReplyEngine:
    """
    AI智能回复引擎
    
    功能：
    1. 意图识别
    2. 知识库检索
    3. 上下文管理
    4. 多模型支持
    5. 智能转人工判断
    """
    
    def __init__(
        self,
        model_provider: str = "openai",
        model_name: str = "gpt-3.5-turbo",
        api_key: str = None,
        api_base: str = None
    ):
        self.model_provider = model_provider
        self.model_name = model_name
        self.api_key = api_key
        self.api_base = api_base
        
        self.knowledge_base = KnowledgeBase()
        self.intent_classifier = IntentClassifier()
        
        # 上下文管理
        self.contexts: Dict[str, CustomerContext] = {}
        
        # 转人工阈值
        self.human_handoff_threshold = 0.6
        
        # 配置
        self.config = {
            "max_context_messages": 10,
            "enable_knowledge_base": True,
            "enable_intent_classification": True,
            "response_temperature": 0.7,
        }
    
    def get_or_create_context(self, customer_id: str, platform: str, shop_id: str, customer_name: str = "") -> CustomerContext:
        """获取或创建客户上下文"""
        context_key = f"{platform}:{shop_id}:{customer_id}"
        
        if context_key not in self.contexts:
            self.contexts[context_key] = CustomerContext(
                customer_id=customer_id,
                customer_name=customer_name,
                platform=platform,
                shop_id=shop_id
            )
        
        return self.contexts[context_key]
    
    async def generate_reply(
        self,
        message: str,
        customer_id: str,
        platform: str,
        shop_id: str,
        customer_name: str = "",
        order_info: Dict[str, Any] = None,
        stream: bool = False
    ) -> AIResponse:
        """
        生成AI回复
        
        Args:
            message: 用户消息
            customer_id: 客户ID
            platform: 平台标识
            shop_id: 店铺ID
            customer_name: 客户名称
            order_info: 关联订单信息
            stream: 是否流式输出
            
        Returns:
            AI回复结果
        """
        # 1. 获取客户上下文
        context = self.get_or_create_context(customer_id, platform, shop_id, customer_name)
        
        # 2. 意图识别
        intent, confidence = self.intent_classifier.classify(message)
        
        # 3. 知识库检索
        knowledge_results = []
        if self.config["enable_knowledge_base"]:
            knowledge_results = await self.knowledge_base.search(message, shop_id)
        
        # 4. 根据意图生成回复
        if intent == MessageIntent.ORDER_INQUIRY and order_info:
            reply_content = self._generate_order_reply(order_info)
        elif intent == MessageIntent.LOGISTICS_INQUIRY and order_info:
            reply_content = self._generate_logistics_reply(order_info)
        elif intent == MessageIntent.GREETING:
            reply_content = self._generate_greeting_reply(context)
        elif knowledge_results and knowledge_results[0]["score"] > 0.7:
            # 使用知识库答案
            reply_content = knowledge_results[0]["answer"]
        else:
            # 使用AI模型生成回复
            reply_content = await self._call_llm(message, context, intent)
        
        # 5. 判断是否需要转人工
        need_human = self._should_handoff_to_human(intent, confidence, message)
        
        # 6. 构建回复结果
        response = AIResponse(
            content=reply_content,
            response_type=ResponseType.NEED_HUMAN if need_human else ResponseType.DIRECT,
            intent=intent,
            confidence=confidence,
            suggested_actions=self._generate_suggested_actions(intent, order_info),
            knowledge_sources=[r["id"] for r in knowledge_results[:3]],
            need_human_review=need_human
        )
        
        # 7. 更新上下文
        context.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        context.conversation_history.append({
            "role": "assistant",
            "content": reply_content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史记录长度
        if len(context.conversation_history) > self.config["max_context_messages"] * 2:
            context.conversation_history = context.conversation_history[-self.config["max_context_messages"] * 2:]
        
        return response
    
    def _generate_order_reply(self, order_info: Dict[str, Any]) -> str:
        """生成订单相关回复"""
        status = order_info.get("status_text", "处理中")
        order_id = order_info.get("platform_order_id", "")
        total = order_info.get("total_amount", 0)
        
        return f"您好！您的订单（{order_id}）当前状态是：{status}，订单金额：¥{total}。如有其他问题请随时联系客服。"
    
    def _generate_logistics_reply(self, order_info: Dict[str, Any]) -> str:
        """生成物流相关回复"""
        tracking = order_info.get("tracking_number", "")
        company = order_info.get("logistics_company", "")
        
        if tracking:
            return f"您的订单已发货，{company} 运单号：{tracking}。您可以到官网查询最新物流信息。"
        else:
            return "您的订单正在准备发货，发货后会第一时间通知您，请耐心等待。"
    
    def _generate_greeting_reply(self, context: CustomerContext) -> str:
        """生成问候回复"""
        greetings = [
            f"您好{context.customer_name}！很高兴为您服务，请问有什么可以帮您的吗？",
            f"亲，欢迎光临！我是您的专属客服，有什么可以帮您的吗？",
            f"您好！请问有什么可以帮您？",
        ]
        
        # 根据VIP等级选择不同问候语
        if context.vip_level == "vip":
            return f"尊敬的VIP客户{context.customer_name}您好！专属客服为您服务~"
        
        import random
        return random.choice(greetings)
    
    async def _call_llm(
        self,
        message: str,
        context: CustomerContext,
        intent: MessageIntent
    ) -> str:
        """
        调用大语言模型
        
        实际实现应调用OpenAI/Claude/文心一言等API
        这里使用模拟实现
        """
        # TODO: 实现实际的LLM调用
        # 根据意图返回默认回复
        default_replies = {
            MessageIntent.PRODUCT_INQUIRY: "感谢您的咨询！这款商品很受欢迎，具体详情可以查看商品页面。如有其他问题请随时联系客服。",
            MessageIntent.PRICE_NEGOTIATION: "亲，我们的价格已经很优惠了，目前店铺还有满减活动，您可以看看其他商品一起购买更划算哦~",
            MessageIntent.AFTER_SALES: "非常抱歉给您带来不好的体验，请您提供一下订单号，我帮您查看处理。",
            MessageIntent.COMPLAINT: "非常抱歉让您不满意，我们会认真对待您的反馈，请您详细说明一下情况，我们会尽快为您处理。",
            MessageIntent.UNKNOWN: "您好，请问您想咨询什么问题呢？我会尽力为您解答。",
        }
        
        return default_replies.get(intent, "您好，请问有什么可以帮您？")
    
    def _should_handoff_to_human(self, intent: MessageIntent, confidence: float, message: str) -> bool:
        """判断是否需要转人工"""
        # 以下情况需要转人工
        if intent == MessageIntent.COMPLAINT:
            return True
        if confidence < 0.4:
            return True
        if "人工" in message or "客服" in message:
            return True
        if "投诉" in message or "举报" in message:
            return True
        
        return False
    
    def _generate_suggested_actions(
        self,
        intent: MessageIntent,
        order_info: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """生成建议操作"""
        actions = []
        
        if intent == MessageIntent.ORDER_INQUIRY:
            actions.append({"type": "view_order", "label": "查看订单", "data": order_info})
        elif intent == MessageIntent.LOGISTICS_INQUIRY:
            actions.append({"type": "track_logistics", "label": "查询物流", "data": order_info})
        elif intent == MessageIntent.AFTER_SALES:
            actions.append({"type": "create_ticket", "label": "创建售后单", "data": {}})
            actions.append({"type": "contact_human", "label": "联系人工", "data": {}})
        
        return actions
    
    async def stream_reply(
        self,
        message: str,
        customer_id: str,
        platform: str,
        shop_id: str,
        customer_name: str = ""
    ) -> AsyncGenerator[str, None]:
        """
        流式生成回复
        
        Yields:
            回复文本片段
        """
        response = await self.generate_reply(
            message, customer_id, platform, shop_id, customer_name
        )
        
        # 模拟流式输出
        words = response.content.split()
        for word in words:
            yield word + " "
    
    def clear_context(self, customer_id: str, platform: str, shop_id: str):
        """清除客户上下文"""
        context_key = f"{platform}:{shop_id}:{customer_id}"
        if context_key in self.contexts:
            del self.contexts[context_key]
    
    def update_config(self, config: Dict[str, Any]):
        """更新配置"""
        self.config.update(config)


# 全局引擎实例
_ai_engine: Optional[AIReplyEngine] = None


def get_ai_engine() -> AIReplyEngine:
    """获取AI引擎单例"""
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = AIReplyEngine()
    return _ai_engine


def init_ai_engine(
    model_provider: str = "openai",
    model_name: str = "gpt-3.5-turbo",
    api_key: str = None,
    api_base: str = None
) -> AIReplyEngine:
    """初始化AI引擎"""
    global _ai_engine
    _ai_engine = AIReplyEngine(
        model_provider=model_provider,
        model_name=model_name,
        api_key=api_key,
        api_base=api_base
    )
    return _ai_engine
