"""
AI算力管理API - 超管后台
结算、收入统计、模型管理
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user
from app.services.ai_power.settlement import SettlementService
from app.services.ai_power.payment import PaymentService
from app.models.ai_power import AIModelPrice, RechargeOrder, AIUsage
from app.models.user import User

router = APIRouter()


@router.get("/admin/ai/revenue")
async def get_platform_revenue(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取平台收入统计（超管）"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="无权限访问")
    
    settlement = SettlementService()
    settlement.db = db
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    stats = await settlement.get_platform_revenue(start_date, end_date)
    return stats


@router.get("/admin/ai/settlements")
async def get_all_settlements(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有结算单（超管）"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="无权限访问")
    
    from app.models.ai_power import ProviderSettlement
    
    query = db.query(ProviderSettlement)
    if status:
        query = query.filter(ProviderSettlement.status == status)
    
    total = query.count()
    items = query.order_by(
        ProviderSettlement.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": str(item.id),
                "provider_id": str(item.provider_id),
                "period_start": item.period_start.isoformat(),
                "period_end": item.period_end.isoformat(),
                "total_usage": float(item.total_usage),
                "platform_cost": float(item.platform_cost),
                "provider_profit": float(item.provider_profit),
                "platform_profit": float(item.platform_profit),
                "status": item.status,
                "created_at": item.created_at.isoformat()
            }
            for item in items
        ]
    }


@router.post("/admin/ai/settlements/{settlement_id}/settle")
async def execute_settlement(
    settlement_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """执行结算（超管）"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="无权限访问")
    
    settlement = SettlementService()
    settlement.db = db
    
    success = await settlement.settle_provider(settlement_id)
    if not success:
        raise HTTPException(status_code=400, detail="结算失败")
    
    return {"message": "结算成功"}


@router.get("/admin/ai/models")
async def get_all_models(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有模型配置（超管）"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="无权限访问")
    
    models = db.query(AIModelPrice).order_by(AIModelPrice.sort_order).all()
    
    return [
        {
            "id": str(m.id),
            "model_name": m.model_name,
            "model_id": m.model_id,
            "provider": m.provider,
            "official_input_price": float(m.official_input_price),
            "official_output_price": float(m.official_output_price),
            "discount_normal": m.discount_normal,
            "discount_bronze": m.discount_bronze,
            "discount_silver": m.discount_silver,
            "discount_gold": m.discount_gold,
            "is_active": m.is_active,
            "is_recommended": m.is_recommended,
            "sort_order": m.sort_order
        }
        for m in models
    ]


@router.post("/admin/ai/models")
async def create_model(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建模型配置（超管）"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="无权限访问")
    
    model = AIModelPrice(
        model_name=data['model_name'],
        model_id=data['model_id'],
        provider=data['provider'],
        official_input_price=data['official_input_price'],
        official_output_price=data['official_output_price'],
        discount_normal=data.get('discount_normal', 100),
        discount_bronze=data.get('discount_bronze', 85),
        discount_silver=data.get('discount_silver', 75),
        discount_gold=data.get('discount_gold', 60),
        is_active=data.get('is_active', True),
        is_recommended=data.get('is_recommended', False),
        sort_order=data.get('sort_order', 0)
    )
    
    db.add(model)
    db.commit()
    db.refresh(model)
    
    return {"id": str(model.id), "message": "创建成功"}


@router.put("/admin/ai/models/{model_id}")
async def update_model(
    model_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新模型配置（超管）"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="无权限访问")
    
    model = db.query(AIModelPrice).filter(AIModelPrice.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    for key, value in data.items():
        if hasattr(model, key):
            setattr(model, key, value)
    
    db.commit()
    db.refresh(model)
    
    return {"message": "更新成功"}


@router.get("/admin/ai/recharge-orders")
async def get_all_recharge_orders(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有充值订单（超管）"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="无权限访问")
    
    query = db.query(RechargeOrder)
    if status:
        query = query.filter(RechargeOrder.status == status)
    
    total = query.count()
    items = query.order_by(
        RechargeOrder.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "order_no": item.order_no,
                "shop_id": str(item.shop_id),
                "amount": float(item.amount),
                "payment_method": item.payment_method,
                "status": item.status,
                "paid_at": item.paid_at.isoformat() if item.paid_at else None,
                "created_at": item.created_at.isoformat()
            }
            for item in items
        ]
    }


@router.get("/admin/ai/usage-overview")
async def get_usage_overview(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用量概览（超管）"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="无权限访问")
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 总用量
    total_usage = db.query(AIUsage).filter(
        AIUsage.created_at >= start_date,
        AIUsage.created_at <= end_date
    )
    
    total_calls = total_usage.count()
    total_tokens = sum(u.total_tokens for u in total_usage.all())
    total_cost = sum(float(u.total_cost) for u in total_usage.all())
    
    # 按模型统计
    model_stats = db.query(
        AIUsage.model_name,
        db.func.count(AIUsage.id).label('calls'),
        db.func.sum(AIUsage.total_tokens).label('tokens'),
        db.func.sum(AIUsage.total_cost).label('cost')
    ).filter(
        AIUsage.created_at >= start_date,
        AIUsage.created_at <= end_date
    ).group_by(AIUsage.model_name).all()
    
    # 按天统计
    daily_stats = db.query(
        db.func.date(AIUsage.created_at).label('date'),
        db.func.count(AIUsage.id).label('calls'),
        db.func.sum(AIUsage.total_cost).label('cost')
    ).filter(
        AIUsage.created_at >= start_date,
        AIUsage.created_at <= end_date
    ).group_by(db.func.date(AIUsage.created_at)).all()
    
    return {
        "period_days": days,
        "total_calls": total_calls,
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "model_stats": [
            {
                "model": stat.model_name,
                "calls": int(stat.calls),
                "tokens": int(stat.tokens or 0),
                "cost": float(stat.cost or 0)
            }
            for stat in model_stats
        ],
        "daily_stats": [
            {
                "date": str(stat.date),
                "calls": int(stat.calls),
                "cost": float(stat.cost or 0)
            }
            for stat in daily_stats
        ]
    }
