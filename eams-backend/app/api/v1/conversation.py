"""
对话管理API - 商户端和客服端使用
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.services.smart_customer_service import get_smart_customer_service

router = APIRouter()


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    buyer_id: str
    message: str
    conversation_id: Optional[str] = None
    product_info: Optional[dict] = None
    order_info: Optional[dict] = None


class SendMessageResponse(BaseModel):
    """发送消息响应"""
    success: bool
    reply: str
    conversation_id: str
    message_id: Optional[str] = None
    usage: Optional[dict] = None
    balance_info: Optional[dict] = None


class ConversationResponse(BaseModel):
    """对话响应"""
    id: str
    buyer_id: str
    buyer_name: Optional[str]
    platform: str
    status: str
    last_message: Optional[str]
    last_message_at: Optional[str]
    unread_count: int
    created_at: str


class MessageResponse(BaseModel):
    """消息响应"""
    id: str
    role: str
    content: str
    ai_model: Optional[str]
    cost: float
    created_at: str


@router.get("/conversations")
async def get_conversations(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    buyer_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取对话列表"""
    # TODO: 从数据库查询
    # 临时返回模拟数据
    conversations = [
        {
            "id": "conv-001",
            "buyer_id": "buyer-001",
            "buyer_name": "张三",
            "platform": "taobao",
            "status": "active",
            "last_message": "这个商品有优惠吗？",
            "last_message_at": "2026-04-18 12:30:00",
            "unread_count": 1,
            "created_at": "2026-04-18 10:00:00"
        },
        {
            "id": "conv-002",
            "buyer_id": "buyer-002",
            "buyer_name": "李四",
            "platform": "jd",
            "status": "handoff",
            "last_message": "我要投诉！",
            "last_message_at": "2026-04-18 11:45:00",
            "unread_count": 0,
            "created_at": "2026-04-18 09:30:00"
        }
    ]
    
    return {
        "total": len(conversations),
        "items": conversations
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation_detail(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取对话详情"""
    return {
        "id": conversation_id,
        "buyer_id": "buyer-001",
        "buyer_name": "张三",
        "platform": "taobao",
        "status": "active",
        "created_at": "2026-04-18 10:00:00"
    }


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    before_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取对话消息历史"""
    service = get_smart_customer_service(db)
    messages = await service.get_conversation_history(conversation_id, limit)
    
    return {
        "conversation_id": conversation_id,
        "total": len(messages),
        "items": messages
    }


@router.post("/conversations/{conversation_id}/send", response_model=SendMessageResponse)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    发送消息（商户主动发送或回复买家）
    
    如果request.message不为空，则作为买家消息处理，AI自动回复
    用于测试或手动触发AI回复
    """
    service = get_smart_customer_service(db)
    
    # TODO: 从current_user获取shop_id
    shop_id = "test-shop-id"
    
    result = await service.handle_buyer_message(
        shop_id=shop_id,
        buyer_id=request.buyer_id,
        buyer_message=request.message,
        conversation_id=conversation_id,
        product_info=request.product_info,
        order_info=request.order_info
    )
    
    return SendMessageResponse(
        success=result["success"],
        reply=result["reply"],
        conversation_id=result["conversation_id"],
        message_id=result.get("message_id"),
        usage=result.get("usage"),
        balance_info=result.get("balance_info")
    )


@router.post("/conversations/{conversation_id}/reply")
async def manual_reply(
    conversation_id: str,
    reply_content: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """人工回复买家"""
    # TODO: 保存人工回复消息
    return {
        "success": True,
        "message": "回复已发送"
    }


@router.post("/conversations/{conversation_id}/handoff")
async def handoff_to_human(
    conversation_id: str,
    reason: str = "买家要求转人工",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """转接人工客服"""
    service = get_smart_customer_service(db)
    success = await service.transfer_to_human(conversation_id, reason)
    
    return {
        "success": success,
        "message": "已转接人工客服" if success else "转接失败"
    }


@router.post("/conversations/{conversation_id}/close")
async def close_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """关闭对话"""
    return {
        "success": True,
        "message": "对话已关闭"
    }


@router.get("/stats/today")
async def get_today_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取今日对话统计"""
    return {
        "total_conversations": 128,
        "active_conversations": 15,
        "ai_replied": 115,
        "handoff_to_human": 13,
        "avg_response_time": 2.5,
        "total_cost": 15.68
    }


@router.get("/stats/usage")
async def get_usage_stats(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取AI用量统计"""
    # TODO: 从current_user获取shop_id
    shop_id = "test-shop-id"
    
    from app.services.ai_power.billing import BillingService
    billing = BillingService()
    stats = await billing.get_usage_stats(shop_id, days)
    
    return stats
