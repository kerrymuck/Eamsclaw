from app.services.ai_adapter import AIProviderAdapter, ADAPTERS
from typing import List, Dict, Any, AsyncGenerator
import httpx
from app.config import get_settings

settings = get_settings()


class AnthropicAdapter(AIProviderAdapter):
    """Anthropic (Claude) 适配器"""
    
    BASE_URL = "https://api.anthropic.com/v1"
    
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
    
    async def chat(self, messages: List[Dict], model: str, **kwargs) -> Dict[str, Any]:
        # 转换消息格式
        system = None
        chat_messages = []
        for m in messages:
            if m.get("role") == "system":
                system = m.get("content")
            else:
                chat_messages.append({
                    "role": m.get("role", "user"),
                    "content": m.get("content", "")
                })
        
        async with httpx.AsyncClient() as client:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            data = {
                "model": model,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "messages": chat_messages
            }
            if system:
                data["system"] = system
            
            response = await client.post(
                f"{self.BASE_URL}/messages",
                headers=headers,
                json=data
            )
            return response.json()
    
    async def chat_stream(self, messages: List[Dict], model: str, **kwargs) -> AsyncGenerator[str, None]:
        yield ""
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        # Claude 3 Opus: 输入 0.015/1K, 输出 0.075/1K
        # Claude 3 Sonnet: 输入 0.003/1K, 输出 0.015/1K
        if "opus" in model:
            return (input_tokens * 0.015 + output_tokens * 0.075) / 1000
        elif "sonnet" in model:
            return (input_tokens * 0.003 + output_tokens * 0.015) / 1000
        return (input_tokens * 0.008 + output_tokens * 0.024) / 1000


class GoogleAdapter(AIProviderAdapter):
    """Google (Gemini) 适配器"""
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
    
    async def chat(self, messages: List[Dict], model: str, **kwargs) -> Dict[str, Any]:
        # 转换消息格式为 Gemini 格式
        contents = []
        for m in messages:
            role = "user" if m.get("role") == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": m.get("content", "")}]
            })
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/models/{model}:generateContent?key={self.api_key}",
                json={"contents": contents}
            )
            return response.json()
    
    async def chat_stream(self, messages: List[Dict], model: str, **kwargs) -> AsyncGenerator[str, None]:
        yield ""
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        # Gemini Pro: 输入 0.0005/1K, 输出 0.0015/1K
        return (input_tokens * 0.0005 + output_tokens * 0.0015) / 1000


class DashscopeAdapter(AIProviderAdapter):
    """阿里云灵积 (通义千问) 适配器"""
    
    BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
    
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
    
    async def chat(self, messages: List[Dict], model: str, **kwargs) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/services/aigc/text-generation/generation",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": model,
                    "input": {"messages": messages},
                    "parameters": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "max_tokens": kwargs.get("max_tokens", 2000)
                    }
                }
            )
            return response.json()
    
    async def chat_stream(self, messages: List[Dict], model: str, **kwargs) -> AsyncGenerator[str, None]:
        yield ""
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        # 通义千问: 输入 0.002/1K, 输出 0.006/1K
        return (input_tokens * 0.002 + output_tokens * 0.006) / 1000


class DoubaoAdapter(AIProviderAdapter):
    """字节豆包 适配器"""
    
    BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
    
    def __init__(self):
        self.api_key = settings.DOUBAO_API_KEY
    
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
        # 豆包: 输入 0.0008/1K, 输出 0.002/1K
        return (input_tokens * 0.0008 + output_tokens * 0.002) / 1000


class YiAdapter(AIProviderAdapter):
    """零一万物 Yi 适配器"""
    
    BASE_URL = "https://api.lingyiwanwu.com/v1"
    
    def __init__(self):
        self.api_key = settings.YI_API_KEY
    
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
        # Yi: 输入 0.002/1K, 输出 0.002/1K
        return (input_tokens * 0.002 + output_tokens * 0.002) / 1000


# 更新适配器注册
ADAPTERS.update({
    "anthropic": AnthropicAdapter,
    "google": GoogleAdapter,
    "dashscope": DashscopeAdapter,
    "doubao": DoubaoAdapter,
    "yi": YiAdapter,
})
