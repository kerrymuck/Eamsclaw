"""
AI调用网关 - 统一封装各模型API调用，集成计费功能
"""

import os
import json
import logging
from typing import Dict, List, Optional, AsyncGenerator, Tuple
from decimal import Decimal
from datetime import datetime
import asyncio

from openai import AsyncOpenAI
import httpx

from app.models.ai_power import AIAccount, AIUsage, AIModelPrice
from app.services.ai_power.billing import BillingService

logger = logging.getLogger(__name__)


class ModelProvider:
    """模型提供商配置"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    BAIDU = "baidu"
    ALIBABA = "alibaba"
    ZHIPU = "zhipu"
    MOONSHOT = "moonshot"
    BYTEDANCE = "bytedance"


class AIGateway:
    """
    AI调用网关
    
    功能：
    1. 统一封装各模型API调用
    2. 自动计量扣费
    3. 余额检查
    4. 用量记录
    """
    
    def __init__(self):
        self.billing_service = BillingService()
        self.clients = {}
        self._init_clients()
    
    def _init_clients(self):
        """初始化各模型客户端"""
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.clients[ModelProvider.OPENAI] = AsyncOpenAI(api_key=openai_key)
            logger.info("OpenAI客户端初始化成功")
        else:
            logger.warning("OpenAI API Key未配置")
        
        # Moonshot (Kimi)
        moonshot_key = os.getenv("MOONSHOT_API_KEY")
        if moonshot_key:
            self.clients[ModelProvider.MOONSHOT] = AsyncOpenAI(
                api_key=moonshot_key,
                base_url="https://api.moonshot.cn/v1"
            )
            logger.info("Moonshot客户端初始化成功")
        else:
            logger.warning("Moonshot API Key未配置")
        
        # 其他模型客户端...（后续添加）
    
    async def chat_completion(
        self,
        shop_id: str,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        conversation_id: Optional[str] = None,
        message_id: Optional[str] = None
    ) -> Dict:
        """
        统一聊天补全接口
        
        Args:
            shop_id: 商户ID
            model_name: 模型名称（如 gpt-4, kimi-k2.5）
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式输出
            conversation_id: 对话ID（用于记录）
            message_id: 消息ID（用于记录）
            
        Returns:
            {
                "success": True/False,
                "data": {...},           # AI响应数据
                "usage": {...},          # Token用量
                "cost": {...},           # 费用信息
                "error": "..."           # 错误信息（如果有）
            }
        """
        try:
            # 1. 获取模型配置和价格
            model_price = await self.billing_service.get_model_price(model_name)
            if not model_price:
                return {
                    "success": False,
                    "error": f"模型 {model_name} 未配置或已禁用"
                }
            
            # 2. 估算所需余额（输入token + 预估输出token）
            input_tokens = self._estimate_tokens(messages)
            estimated_output_tokens = max_tokens or 1000
            estimated_cost = self._calculate_cost(
                model_price, input_tokens, estimated_output_tokens
            )
            
            # 3. 检查余额
            has_balance, balance_info = await self.billing_service.check_balance(
                shop_id, estimated_cost
            )
            if not has_balance:
                return {
                    "success": False,
                    "error": "余额不足",
                    "balance": float(balance_info.get("available", 0)),
                    "need_recharge": True
                }
            
            # 4. 调用AI API
            provider = model_price.provider
            model_id = model_price.model_id
            
            start_time = datetime.utcnow()
            
            if provider == ModelProvider.OPENAI or provider == ModelProvider.MOONSHOT:
                response = await self._call_openai_compatible(
                    provider, model_id, messages, temperature, max_tokens
                )
            elif provider == ModelProvider.ANTHROPIC:
                response = await self._call_anthropic(
                    model_id, messages, temperature, max_tokens
                )
            elif provider == ModelProvider.BAIDU:
                response = await self._call_baidu(
                    model_id, messages, temperature, max_tokens
                )
            else:
                return {
                    "success": False,
                    "error": f"暂不支持的模型提供商: {provider}"
                }
            
            response_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # 5. 计算实际费用
            usage = response.get("usage", {})
            actual_input_tokens = usage.get("prompt_tokens", input_tokens)
            actual_output_tokens = usage.get("completion_tokens", 0)
            
            actual_cost = self._calculate_cost(
                model_price, actual_input_tokens, actual_output_tokens
            )
            
            # 6. 扣除余额
            deduct_success = await self.billing_service.deduct_balance(
                shop_id=shop_id,
                amount=actual_cost,
                model_name=model_name,
                input_tokens=actual_input_tokens,
                output_tokens=actual_output_tokens,
                conversation_id=conversation_id,
                message_id=message_id,
                response_time_ms=response_time_ms
            )
            
            if not deduct_success:
                logger.error(f"扣费失败: shop_id={shop_id}, amount={actual_cost}")
            
            return {
                "success": True,
                "data": response,
                "usage": {
                    "input_tokens": actual_input_tokens,
                    "output_tokens": actual_output_tokens,
                    "total_tokens": actual_input_tokens + actual_output_tokens
                },
                "cost": {
                    "input_cost": float(actual_cost["input_cost"]),
                    "output_cost": float(actual_cost["output_cost"]),
                    "total_cost": float(actual_cost["total_cost"])
                }
            }
            
        except Exception as e:
            logger.error(f"AI调用失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _call_openai_compatible(
        self,
        provider: str,
        model_id: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> Dict:
        """调用OpenAI兼容接口（OpenAI、Moonshot等）"""
        client = self.clients.get(provider)
        if not client:
            raise ValueError(f"{provider} 客户端未初始化")
        
        params = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        
        response = await client.chat.completions.create(**params)
        
        return {
            "id": response.id,
            "model": response.model,
            "choices": [
                {
                    "index": choice.index,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content
                    },
                    "finish_reason": choice.finish_reason
                }
                for choice in response.choices
            ],
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    
    async def _call_anthropic(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> Dict:
        """调用Anthropic Claude API"""
        # TODO: 实现Claude API调用
        raise NotImplementedError("Claude API调用待实现")
    
    async def _call_baidu(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> Dict:
        """调用百度文心一言API"""
        # TODO: 实现百度API调用
        raise NotImplementedError("百度API调用待实现")
    
    def _estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        估算输入token数
        简单估算：1个汉字≈2个token，1个英文单词≈1.3个token
        """
        total_chars = 0
        for msg in messages:
            content = msg.get("content", "")
            total_chars += len(content)
        
        # 粗略估算：平均1.5 token/字符
        return int(total_chars * 1.5)
    
    async def chat_completion_stream(
        self,
        shop_id: str,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """
        流式聊天补全接口（SSE）
        
        Yields:
            {"type": "content", "content": "..."}
            {"type": "usage", "usage": {...}, "cost": {...}}
        """
        try:
            # 获取模型配置
            model_price = await self.billing_service.get_model_price(model_name)
            if not model_price:
                yield {"type": "error", "error": f"模型 {model_name} 未配置"}
                return
            
            provider = model_price.provider
            model_id = model_price.model_id
            
            # 估算输入token
            input_tokens = self._estimate_tokens(messages)
            
            # 调用流式API
            if provider == ModelProvider.OPENAI or provider == ModelProvider.MOONSHOT:
                client = self.clients.get(provider)
                if not client:
                    yield {"type": "error", "error": f"{provider} 客户端未初始化"}
                    return
                
                params = {
                    "model": model_id,
                    "messages": messages,
                    "temperature": temperature,
                    "stream": True
                }
                if max_tokens:
                    params["max_tokens"] = max_tokens
                
                full_content = ""
                output_tokens = 0
                
                async for chunk in await client.chat.completions.create(**params):
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_content += content
                        output_tokens += len(content) // 2  # 粗略估算
                        yield {"type": "content", "content": content}
                
                # 计算费用
                actual_cost = self._calculate_cost(
                    model_price, input_tokens, output_tokens
                )
                
                # 扣除余额
                await self.billing_service.deduct_balance(
                    shop_id=shop_id,
                    amount=actual_cost,
                    model_name=model_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens
                )
                
                yield {
                    "type": "usage",
                    "usage": {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens
                    },
                    "cost": {
                        "input_cost": float(actual_cost["input_cost"]),
                        "output_cost": float(actual_cost["output_cost"]),
                        "total_cost": float(actual_cost["total_cost"])
                    }
                }
            else:
                yield {"type": "error", "error": f"流式输出暂不支持 {provider}"}
                
        except Exception as e:
            logger.error(f"流式AI调用失败: {e}", exc_info=True)
            yield {"type": "error", "error": str(e)}
    
    def _calculate_cost(
        self,
        model_price: AIModelPrice,
        input_tokens: int,
        output_tokens: int
    ) -> Dict[str, Decimal]:
        """
        计算费用
        
        价格单位：元/千token
        """
        input_price_per_1k = Decimal(str(model_price.official_input_price))
        output_price_per_1k = Decimal(str(model_price.official_output_price))
        
        input_cost = (Decimal(input_tokens) / 1000) * input_price_per_1k
        output_cost = (Decimal(output_tokens) / 1000) * output_price_per_1k
        
        return {
            "input_cost": input_cost.quantize(Decimal("0.0001")),
            "output_cost": output_cost.quantize(Decimal("0.0001")),
            "total_cost": (input_cost + output_cost).quantize(Decimal("0.0001"))
        }


# 全局网关实例
_ai_gateway: Optional[AIGateway] = None


def get_ai_gateway() -> AIGateway:
    """获取AI网关单例"""
    global _ai_gateway
    if _ai_gateway is None:
        _ai_gateway = AIGateway()
    return _ai_gateway
