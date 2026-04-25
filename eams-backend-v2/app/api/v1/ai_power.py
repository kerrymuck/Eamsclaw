from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.base import success_response
from app.middlewares.auth import require_merchant
from app.services.ai import ai_model_service, ai_usage_service
from decimal import Decimal

router = APIRouter()


class AIChatRequest(BaseModel):
    model: str
    messages: List[dict]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None


@router.get("/models")
async def list_models(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_merchant)
):
    """获取可用模型列表"""
    models = await ai_model_service.get_active_models(db)
    
    return success_response([
        {
            "id": f"{m.provider.value}/{m.model_id}",
            "name": m.model_name,
            "provider": m.provider.value,
            "input_price": float(m.input_price),
            "output_price": float(m.output_price),
            "max_tokens": m.max_tokens,
            "response_time": m.response_time,
            "accuracy": m.accuracy,
            "star_rating": m.star_rating
        }
        for m in models
    ])


@router.get("/account")
async def get_account_info(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_merchant)
):
    """获取AI账户信息"""
    # TODO: 从token获取商户ID
    merchant_id = 1
    
    stats = await ai_usage_service.get_usage_statistics(db, merchant_id, days=30)
    
    return success_response({
        "balance": 1000.00,
        "total_usage": float(stats["total_cost"]),
        "today_usage": 0,
        "month_usage": float(stats["total_cost"]),
        "total_tokens": stats["total_tokens"],
        "total_calls": stats["total_calls"]
    })


@router.get("/usage")
async def get_usage_stats(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_merchant)
):
    """获取使用统计"""
    # TODO: 从token获取商户ID
    merchant_id = 1
    
    stats = await ai_usage_service.get_usage_statistics(db, merchant_id, days=days)
    return success_response(stats)


@router.post("/chat")
async def chat(
    request: AIChatRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_merchant)
):
    """AI对话"""
    # TODO: 实现真实AI调用
    # TODO: 从token获取商户ID
    merchant_id = 1
    
    # 模拟响应
    import uuid
    request_tokens = sum(len(m.get("content", "")) for m in request.messages) // 4
    response_tokens = 50
    total_tokens = request_tokens + response_tokens
    cost = Decimal("0.001") * (total_tokens / 1000)
    
    # 记录使用
    await ai_usage_service.create_usage_record(
        db,
        merchant_id=merchant_id,
        model_id=request.model,
        request_tokens=request_tokens,
        response_tokens=response_tokens,
        cost=cost,
        request_id=str(uuid.uuid4())
    )
    
    return success_response({
        "id": str(uuid.uuid4()),
        "model": request.model,
        "content": "这是一个模拟响应。实际环境中将调用对应的AI API。",
        "usage": {
            "prompt_tokens": request_tokens,
            "completion_tokens": response_tokens,
            "total_tokens": total_tokens,
            "cost": float(cost)
        }
    })


@router.get("/usage/records")
async def get_usage_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_merchant)
):
    """获取使用记录"""
    # TODO: 从token获取商户ID
    merchant_id = 1
    
    from datetime import datetime, timedelta
    start_date = datetime.now() - timedelta(days=30)
    
    records = await ai_usage_service.get_merchant_usage(db, merchant_id, start_date)
    
    return success_response({
        "total": len(records),
        "page": page,
        "page_size": page_size,
        "pages": 1,
        "items": [r.to_dict() for r in records]
    })
