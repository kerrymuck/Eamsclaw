"""
服务商结算API - 服务商后台结算查询
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user
from app.services.ai_power.settlement import SettlementService
from app.models.user import User

router = APIRouter()


@router.get("/provider/ai/settlements")
async def get_provider_settlements(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取服务商结算列表"""
    if current_user.role != 'provider':
        raise HTTPException(status_code=403, detail="无权限访问")
    
    settlement = SettlementService()
    settlement.db = db
    
    result = await settlement.get_provider_settlements(
        provider_id=str(current_user.id),
        status=status,
        page=page,
        page_size=page_size
    )
    
    return result


@router.get("/provider/ai/settlement-detail/{settlement_id}")
async def get_settlement_detail(
    settlement_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取结算详情"""
    if current_user.role != 'provider':
        raise HTTPException(status_code=403, detail="无权限访问")
    
    from app.models.ai_power import ProviderSettlement
    
    settlement = db.query(ProviderSettlement).filter(
        ProviderSettlement.id == settlement_id,
        ProviderSettlement.provider_id == current_user.id
    ).first()
    
    if not settlement:
        raise HTTPException(status_code=404, detail="结算单不存在")
    
    return {
        "id": str(settlement.id),
        "period_start": settlement.period_start.isoformat(),
        "period_end": settlement.period_end.isoformat(),
        "total_usage": float(settlement.total_usage),
        "platform_cost": float(settlement.platform_cost),
        "provider_profit": float(settlement.provider_profit),
        "platform_profit": float(settlement.platform_profit),
        "status": settlement.status,
        "settled_at": settlement.settled_at.isoformat() if settlement.settled_at else None,
        "created_at": settlement.created_at.isoformat()
    }


@router.get("/provider/ai/revenue")
async def get_provider_revenue(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取服务商收入统计"""
    if current_user.role != 'provider':
        raise HTTPException(status_code=403, detail="无权限访问")
    
    settlement = SettlementService()
    settlement.db = db
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 计算预估收入
    stats = await settlement.calculate_provider_settlement(
        provider_id=str(current_user.id),
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "period_days": days,
        "estimated_revenue": stats["provider_profit"],
        "total_usage": stats["total_usage"],
        "shop_count": stats["shop_count"],
        "model_breakdown": stats["details"]
    }
