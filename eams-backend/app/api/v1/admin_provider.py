"""
服务商管理API
用于超管后台管理服务商
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter()


class ProviderResponse(BaseModel):
    """服务商响应"""
    id: str
    name: str
    contact: str
    phone: str
    email: str
    level: str
    license_count: int
    balance: float
    status: str
    create_time: str
    
    class Config:
        from_attributes = True


class ProviderListResponse(BaseModel):
    """服务商列表响应"""
    total: int
    items: List[ProviderResponse]


class BlacklistItem(BaseModel):
    """黑名单项"""
    id: str
    name: str
    contact: str
    phone: str
    reason: str
    remark: str
    blacklist_time: str
    operator: str


@router.get("/providers", response_model=ProviderListResponse)
async def get_providers(
    name: Optional[str] = None,
    status: Optional[str] = None,
    level: Optional[str] = None,
    time_range: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取服务商列表（带筛选）"""
    # 模拟数据 - 实际应从数据库查询
    providers = [
        {
            "id": "1",
            "name": "科技云",
            "contact": "张三",
            "phone": "13800138001",
            "email": "zhangsan@kejiyun.com",
            "level": "gold",
            "license_count": 156,
            "balance": 125800,
            "status": "active",
            "create_time": "2026-01-15 10:30:00"
        },
        {
            "id": "2",
            "name": "智慧零售",
            "contact": "李四",
            "phone": "13800138002",
            "email": "lisi@zhihui.com",
            "level": "silver",
            "license_count": 89,
            "balance": 67800,
            "status": "active",
            "create_time": "2026-01-20 14:20:00"
        },
        {
            "id": "3",
            "name": "未来电商",
            "contact": "王五",
            "phone": "13800138003",
            "email": "wangwu@weilai.com",
            "level": "bronze",
            "license_count": 45,
            "balance": 23400,
            "status": "pending",
            "create_time": "2026-03-01 09:00:00"
        }
    ]
    
    # 筛选逻辑
    if name:
        providers = [p for p in providers if name.lower() in p["name"].lower()]
    if status:
        providers = [p for p in providers if p["status"] == status]
    if level:
        providers = [p for p in providers if p["level"] == level]
    
    # 时间筛选
    if time_range:
        now = datetime.now()
        if time_range == "today":
            start = now.replace(hour=0, minute=0, second=0)
        elif time_range == "thisMonth":
            start = now.replace(day=1, hour=0, minute=0, second=0)
        elif time_range == "last30Days":
            start = now - timedelta(days=30)
        elif time_range == "last90Days":
            start = now - timedelta(days=90)
        elif time_range == "last6Months":
            start = now - timedelta(days=180)
        elif time_range == "last1Year":
            start = now - timedelta(days=365)
        else:
            start = None
        
        if start:
            providers = [p for p in providers if datetime.strptime(p["create_time"], "%Y-%m-%d %H:%M:%S") >= start]
    
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        providers = [p for p in providers if start <= datetime.strptime(p["create_time"], "%Y-%m-%d %H:%M:%S") < end]
    
    total = len(providers)
    # 分页
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    providers = providers[start_idx:end_idx]
    
    return {
        "total": total,
        "items": providers
    }


@router.get("/providers/blacklist")
async def get_blacklist(
    name: Optional[str] = None,
    reason: Optional[str] = None,
    time_range: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取服务商黑名单"""
    blacklist = [
        {
            "id": "1",
            "name": "问题服务商A",
            "contact": "张三",
            "phone": "13800138001",
            "reason": "violation",
            "remark": "多次违规操作，恶意刷单",
            "blacklist_time": "2026-03-15 14:30:00",
            "operator": "admin"
        },
        {
            "id": "2",
            "name": "欠费服务商B",
            "contact": "李四",
            "phone": "13800138002",
            "reason": "arrears",
            "remark": "欠费超过3个月",
            "blacklist_time": "2026-02-20 10:15:00",
            "operator": "admin"
        },
        {
            "id": "3",
            "name": "投诉服务商C",
            "contact": "王五",
            "phone": "13800138003",
            "reason": "complaint",
            "remark": "客户投诉过多，服务态度差",
            "blacklist_time": "2026-01-10 16:45:00",
            "operator": "admin"
        }
    ]
    
    # 筛选逻辑
    if name:
        blacklist = [b for b in blacklist if name.lower() in b["name"].lower()]
    if reason:
        blacklist = [b for b in blacklist if b["reason"] == reason]
    
    # 时间筛选
    if time_range:
        now = datetime.now()
        if time_range == "today":
            start = now.replace(hour=0, minute=0, second=0)
        elif time_range == "thisMonth":
            start = now.replace(day=1, hour=0, minute=0, second=0)
        elif time_range == "last30Days":
            start = now - timedelta(days=30)
        elif time_range == "last90Days":
            start = now - timedelta(days=90)
        elif time_range == "last6Months":
            start = now - timedelta(days=180)
        elif time_range == "last1Year":
            start = now - timedelta(days=365)
        else:
            start = None
        
        if start:
            blacklist = [b for b in blacklist if datetime.strptime(b["blacklist_time"], "%Y-%m-%d %H:%M:%S") >= start]
    
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        blacklist = [b for b in blacklist if start <= datetime.strptime(b["blacklist_time"], "%Y-%m-%d %H:%M:%S") < end]
    
    total = len(blacklist)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    blacklist = blacklist[start_idx:end_idx]
    
    return {
        "total": total,
        "items": blacklist
    }


@router.post("/providers/blacklist/remove")
async def remove_from_blacklist(
    provider_ids: List[str],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """批量移出黑名单"""
    return {
        "success": True,
        "message": f"成功移出 {len(provider_ids)} 个服务商"
    }


@router.post("/providers/{provider_id}/recharge")
async def recharge_provider(
    provider_id: str,
    amount: float,
    remark: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """为服务商充值"""
    return {
        "success": True,
        "message": f"充值 ¥{amount} 成功",
        "provider_id": provider_id
    }


@router.post("/providers/{provider_id}/toggle-status")
async def toggle_provider_status(
    provider_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """切换服务商状态"""
    return {
        "success": True,
        "message": "状态切换成功",
        "provider_id": provider_id
    }
