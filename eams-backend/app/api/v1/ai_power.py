"""
AI算力API - 商户端AI账户、充值、用量查询
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from app.api.deps import get_db, get_current_shop
from app.services.ai_power.billing import BillingService
from app.services.ai_power.payment import PaymentService
from app.services.ai.gateway import get_ai_gateway
from app.schemas.ai_power import (
    AIAccountInfo, RechargeCreate, RechargeResponse,
    UsageStats, ModelInfo, ChatRequest, ChatResponse
)

router = APIRouter()


@router.get("/account", response_model=AIAccountInfo)
async def get_account_info(
    shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    """获取AI账户信息"""
    billing = BillingService()
    billing.db = db
    
    info = await billing.get_account_info(str(shop.id))
    return AIAccountInfo(**info)


@router.post("/recharge", response_model=RechargeResponse)
async def create_recharge_order(
    request: RechargeCreate,
    shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    """创建充值订单"""
    payment = PaymentService()
    payment.db = db
    
    result = await payment.create_recharge_order(
        shop_id=str(shop.id),
        amount=Decimal(str(request.amount)),
        payment_method=request.payment_method
    )
    
    return RechargeResponse(
        order_no=result["order_no"],
        amount=result["amount"],
        payment_url=result["payment_url"],
        status="pending"
    )


@router.get("/usage", response_model=UsageStats)
async def get_usage_statistics(
    days: int = 30,
    shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    """获取用量统计"""
    billing = BillingService()
    billing.db = db
    
    stats = await billing.get_usage_stats(str(shop.id), days)
    return UsageStats(**stats)


@router.get("/usage/details")
async def get_usage_details(
    page: int = 1,
    page_size: int = 20,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    """获取用量明细"""
    from app.models.ai_power import AIUsage
    
    query = db.query(AIUsage).filter(AIUsage.shop_id == shop.id)
    
    if start_date:
        query = query.filter(AIUsage.created_at >= start_date)
    if end_date:
        query = query.filter(AIUsage.created_at <= end_date)
    
    total = query.count()
    items = query.order_by(AIUsage.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": str(item.id),
                "model_name": item.model_name,
                "input_tokens": item.input_tokens,
                "output_tokens": item.output_tokens,
                "total_cost": float(item.total_cost),
                "created_at": item.created_at.isoformat()
            }
            for item in items
        ]
    }


@router.get("/models", response_model=List[ModelInfo])
async def get_available_models(
    db: Session = Depends(get_db)
):
    """获取可用模型列表"""
    billing = BillingService()
    billing.db = db
    
    models = await billing.get_available_models()
    return [ModelInfo(**m) for m in models]


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    """
    AI聊天接口（带计费）
    
    这是主要的AI调用入口，会自动：
    1. 检查余额
    2. 调用AI API
    3. 计量扣费
    4. 记录用量
    """
    gateway = get_ai_gateway()
    
    result = await gateway.chat_completion(
        shop_id=str(shop.id),
        model_name=request.model,
        messages=request.messages,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        conversation_id=request.conversation_id,
        message_id=request.message_id
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=402 if result.get("need_recharge") else 400,
            detail=result["error"]
        )
    
    return ChatResponse(
        content=result["data"]["choices"][0]["message"]["content"],
        model=request.model,
        usage=result["usage"],
        cost=result["cost"]
    )


@router.get("/transactions")
async def get_transactions(
    page: int = 1,
    page_size: int = 20,
    shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    """获取交易记录"""
    from app.models.ai_power import AITransaction
    
    query = db.query(AITransaction).filter(
        AITransaction.shop_id == shop.id
    )
    
    total = query.count()
    items = query.order_by(AITransaction.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": str(item.id),
                "type": item.type,
                "amount": float(item.amount),
                "balance_after": float(item.balance_after),
                "description": item.description,
                "created_at": item.created_at.isoformat()
            }
            for item in items
        ]
    }
