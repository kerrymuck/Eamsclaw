import os
from typing import List, Dict, Optional, AsyncGenerator
from openai import AsyncOpenAI
import json
import logging

logger = logging.getLogger(__name__)


class AIService:
    """AI服务核心类"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        
        # 默认参数
        self.default_temperature = 0.7
        self.default_max_tokens = 500
        
    async def classify_intent(
        self, 
        text: str, 
        context: Optional[List[Dict]] = None,
        candidate_intents: Optional[List[str]] = None
    ) -> Dict:
        """
        意图识别
        
        Args:
            text: 用户输入文本
            context: 对话上下文
            candidate_intents: 候选意图列表
            
        Returns:
            {
                "intent": "意图名称",
                "confidence": 0.95,
                "alternatives": [{"intent": "xxx", "confidence": 0.3}]
            }
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return {"intent": "unknown", "confidence": 0.0, "alternatives": []}
        
        try:
            # 构建提示词
            system_prompt = self._get_intent_system_prompt(candidate_intents)
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加上下文
            if context:
                for msg in context[-5:]:  # 最近5条
                    role = "user" if msg.get("direction") == "in" else "assistant"
                    messages.append({"role": role, "content": msg.get("content", "")})
            
            messages.append({"role": "user", "content": text})
            
            # 调用API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # 意图识别用低temperature
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "intent": result.get("intent", "unknown"),
                "confidence": float(result.get("confidence", 0)),
                "alternatives": result.get("alternatives", [])
            }
            
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return {"intent": "unknown", "confidence": 0.0, "alternatives": []}
    
    async def generate_reply(
        self,
        text: str,
        intent: str,
        context: Optional[List[Dict]] = None,
        knowledge_items: Optional[List[Dict]] = None,
        shop_info: Optional[Dict] = None
    ) -> Dict:
        """
        生成回复
        
        Args:
            text: 用户输入
            intent: 识别到的意图
            context: 对话上下文
            knowledge_items: 相关知识库条目
            shop_info: 店铺信息
            
        Returns:
            {
                "content": "回复内容",
                "type": "text",
                "suggested_actions": []
            }
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return {
                "content": "抱歉，我暂时无法回答，请稍后再试。",
                "type": "text",
                "suggested_actions": []
            }
        
        try:
            # 构建系统提示词
            system_prompt = self._get_reply_system_prompt(shop_info, knowledge_items)
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加上下文
            if context:
                for msg in context[-10:]:  # 最近10条
                    role = "user" if msg.get("direction") == "in" else "assistant"
                    messages.append({"role": role, "content": msg.get("content", "")})
            
            # 添加当前消息
            messages.append({"role": "user", "content": f"[意图: {intent}] {text}"})
            
            # 调用API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.default_temperature,
                max_tokens=self.default_max_tokens
            )
            
            content = response.choices[0].message.content
            
            return {
                "content": content,
                "type": "text",
                "suggested_actions": []
            }
            
        except Exception as e:
            logger.error(f"Reply generation error: {e}")
            return {
                "content": "抱歉，我暂时无法回答，请稍后再试。",
                "type": "text",
                "suggested_actions": ["转人工"]
            }
    
    async def should_handoff(
        self,
        text: str,
        intent: str,
        context: Optional[List[Dict]] = None
    ) -> Dict:
        """
        判断是否需要转人工
        
        Returns:
            {
                "should_handoff": True/False,
                "reason": "原因"
            }
        """
        # 简单规则判断
        handoff_intents = ["complaint", "refund_request", "complex_issue", "human_request"]
        
        if intent in handoff_intents:
            return {"should_handoff": True, "reason": intent}
        
        # 检查是否明确要求人工
        handoff_keywords = ["人工", "客服", "找人工", "转人工", "人工客服", "投诉"]
        if any(kw in text for kw in handoff_keywords):
            return {"should_handoff": True, "reason": "user_request"}
        
        return {"should_handoff": False, "reason": None}
    
    def _get_intent_system_prompt(self, candidate_intents: Optional[List[str]] = None) -> str:
        """获取意图识别系统提示词"""
        base_intents = [
            "shipping_inquiry",  # 物流查询
            "product_inquiry",   # 商品咨询
            "price_inquiry",     # 价格咨询
            "stock_inquiry",     # 库存查询
            "return_request",    # 退货申请
            "refund_request",    # 退款申请
            "exchange_request",  # 换货申请
            "complaint",         # 投诉
            "human_request",     # 要求人工
            "greeting",          # 问候
            "goodbye",           # 告别
            "thanks",            # 感谢
            "other"              # 其他
        ]
        
        if candidate_intents:
            intents = candidate_intents
        else:
            intents = base_intents
        
        return f"""你是一个电商客服意图识别助手。请分析用户输入，识别其意图。

可选意图：{', '.join(intents)}

请按以下JSON格式返回：
{{
    "intent": "意图名称",
    "confidence": 0.95,
    "alternatives": [
        {{"intent": "备选意图1", "confidence": 0.3}},
        {{"intent": "备选意图2", "confidence": 0.1}}
    ]
}}

注意：
- confidence 范围 0-1
- 只从可选意图中选择
- 如果不确定，选择 confidence 较低但最接近的"""
    
    def _get_reply_system_prompt(
        self, 
        shop_info: Optional[Dict] = None,
        knowledge_items: Optional[List[Dict]] = None
    ) -> str:
        """获取回复生成系统提示词"""
        shop_name = shop_info.get("name", "本店") if shop_info else "本店"
        
        prompt = f"""你是{shop_name}的AI客服助手，请用友好、专业的语气回复顾客。

回复原则：
1. 语气亲切友好，使用"亲"、"您好"等礼貌用语
2. 回答简洁明了，控制在100字以内
3. 如果不确定，引导顾客联系人工客服
4. 涉及退款/投诉等敏感问题，建议转人工
"""
        
        # 添加知识库信息
        if knowledge_items:
            prompt += "\n\n参考知识库信息：\n"
            for item in knowledge_items[:3]:
                prompt += f"Q: {item.get('question', '')}\nA: {item.get('answer', '')}\n\n"
        
        return prompt


# 全局AI服务实例
ai_service = AIService()
