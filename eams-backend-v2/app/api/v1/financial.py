from fastapi import APIRouter, Depends, Query
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.base import success_response
from app.middlewares.auth import require_super_admin
from app.services.payment import recharge_service, financial_service
from app.services.ai import ai_usage_service

router = APIRouter()


@router.get("/account")
async def get_account_info(
    db: AsyncSession = Depends(get_db)
):
    """获取AI账户信息"""
    # TODO: 从token获取商户ID
    merchant_id = 1
    
    # 获取使用统计
    stats = await ai_usage_service.get_usage_statistics(db, merchant_id, days=30)
    
    return success_response({
        "balance": 1000.00,  # TODO: 从商户表获取
        "total_usage": stats["total_cost"],
        "today_usage": 0,
        "month_usage": stats["total_cost"],
        "total_tokens": stats["total_tokens"],
        "total_calls": stats["total_calls"]
    })


@router.get("/usage")
async def get_usage_stats(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """获取使用统计"""
    # TODO: 从token获取商户ID
    merchant_id = 1
    
    stats = await ai_usage_service.get_usage_statistics(db, merchant_id, days=days)
    return success_response(stats)


@router.get("/orders")
async def list_recharge_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取充值记录"""
    # TODO: 从token获取商户ID
    merchant_id = 1
    
    skip = (page - 1) * page_size
    orders = await recharge_service.get_merchant_orders(db, merchant_id, skip, page_size, status)
    
    return success_response({
        "total": len(orders),
        "page": page,
        "page_size": page_size,
        "pages": 1,
        "items": [o.to_dict() for o in orders]
    })


@router.get("/financial")
async def list_financial_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    record_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取财务流水"""
    # TODO: 从token获取商户ID
    merchant_id = 1
    
    skip = (page - 1) * page_size
    records = await financial_service.get_merchant_records(db, merchant_id, skip, page_size, record_type)
    
    return success_response({
        "total": len(records),
        "page": page,
        "page_size": page_size,
        "pages": 1,
        "items": [r.to_dict() for r in records]
    })


@router.get("/financial/statistics")
async def get_financial_statistics(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """获取财务统计"""
    # TODO: 从token获取商户ID
    merchant_id = 1
    
    stats = await financial_service.get_statistics(db, merchant_id, days)
    return success_response(stats)
