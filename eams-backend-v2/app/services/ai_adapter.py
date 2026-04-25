# AI 服务适配器

from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator
import httpx
from app.config import get_settings

settings = get_settings()


class AIProviderAdapter(ABC):
    """AI提供商适配器基类"""
    
    @abstractmethod
    async def chat(self, messages: List[Dict], model: str, **kwargs) -> Dict[str, Any]:
        """对话接口"""
        pass
    
    @abstractmethod
    async def chat_stream(self, messages: List[Dict], model: str, **kwargs) -> AsyncGenerator[str, None]:
        """流式对话接口"""
        pass
    
    @abstractmethod
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """计算费用"""
        pass


class MoonshotAdapter(AIProviderAdapter):
    """Moonshot (Kimi) 适配器"""
    
    BASE_URL = "https://api.moonshot.cn/v1"
    
    def __init__(self):
        self.api_key = settings.MOONSHOT_API_KEY
    
    async def chat(self, messages: List[Dict], model: str, **kwargs) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 2000)
                }
            )
            return response.json()
    
    async def chat_stream(self, messages: List[Dict], model: str, **kwargs) -> AsyncGenerator[str, None]:
        # TODO: 实现流式响应
        yield ""
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        # Kimi K2.5: 输入 0.001/1K, 输出 0.002/1K
        return (input_tokens * 0.001 + output_tokens * 0.002) / 1000


class OpenAIAdapter(AIProviderAdapter):
    """OpenAI 适配器"""
    
    BASE_URL = "https://api.openai.com/v1"
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
    
    async def chat(self, messages: List[Dict], model: str, **kwargs) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 2000)
                }
            )
            return response.json()
    
    async def chat_stream(self, messages: List[Dict], model: str, **kwargs) -> AsyncGenerator[str, None]:
        yield ""
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        # GPT-4: 输入 0.03/1K, 输出 0.06/1K
        return (input_tokens * 0.03 + output_tokens * 0.06) / 1000


class DeepSeekAdapter(AIProviderAdapter):
    """DeepSeek 适配器"""
    
    BASE_URL = "https://api.deepseek.com/v1"
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
    
    async def chat(self, messages: List[Dict], model: str, **kwargs) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.7)
                }
            )
            return response.json()
    
    async def chat_stream(self, messages: List[Dict], model: str, **kwargs) -> AsyncGenerator[str, None]:
        yield ""
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        return (input_tokens * 0.001 + output_tokens * 0.002) / 1000


# 适配器工厂
ADAPTERS = {
    "moonshot": MoonshotAdapter,
    "openai": OpenAIAdapter,
    "deepseek": DeepSeekAdapter,
    "anthropic": None,  # 从 ai_adapter_extra 导入
    "google": None,
    "dashscope": None,
    "doubao": None,
    "yi": None,
}


def get_adapter(provider: str) -> AIProviderAdapter:
    """获取适配器实例"""
    # 先尝试从主模块获取
    adapter_class = ADAPTERS.get(provider)
    
    # 如果主模块没有，尝试从扩展模块导入
    if adapter_class is None:
        try:
            from app.services.ai_adapter_extra import ADAPTERS as EXTRA_ADAPTERS
            adapter_class = EXTRA_ADAPTERS.get(provider)
        except ImportError:
            pass
    
    if not adapter_class:
        raise ValueError(f"不支持的AI提供商: {provider}")
    
    return adapter_class()
