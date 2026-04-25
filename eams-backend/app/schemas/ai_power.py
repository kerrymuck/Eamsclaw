"""
AI算力相关数据模型Schema
"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class AIAccountInfo(BaseModel):
    """AI账户信息"""
    balance: float
    free_quota: float
    total_available: float
    total_recharged: float
    total_consumed: float
    status: str


class RechargeCreate(BaseModel):
    """创建充值订单请求"""
    amount: float
    payment_method: str  # alipay/wechat/bank


class RechargeResponse(BaseModel):
    """充值订单响应"""
    order_no: str
    amount: float
    payment_url: str
    status: str


class UsageStats(BaseModel):
    """用量统计"""
    period_days: int
    total_tokens: int
    total_cost: float
    total_calls: int
    avg_cost_per_call: float
    model_breakdown: Dict


class ModelInfo(BaseModel):
    """模型信息"""
    id: str
    name: str
    provider: str
    input_price: float
    output_price: float
    features: List[str]
    icon: str
    context_length: Optional[int]
    max_tokens: Optional[int]


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # system/user/assistant
    content: str


class ChatRequest(BaseModel):
    """聊天请求"""
    model: str
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None


class TokenUsage(BaseModel):
    """Token用量"""
    input_tokens: int
    output_tokens: int
    total_tokens: int


class CostInfo(BaseModel):
    """费用信息"""
    input_cost: float
    output_cost: float
    total_cost: float


class ChatResponse(BaseModel):
    """聊天响应"""
    content: str
    model: str
    usage: TokenUsage
    cost: CostInfo
