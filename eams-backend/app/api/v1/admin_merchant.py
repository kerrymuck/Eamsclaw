"""
超管后台 - 商户管理API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user

router = APIRouter()


class MerchantResponse(BaseModel):
    """商户响应"""
    id: str
    name: str
    logo: Optional[str]
    provider_id: str
    provider_name: str
    plan_type: str
    plan_name: str
    max_shops: int
    shop_count: int
    expire_date: str
    contact_name: str
    contact_phone: str
    contact_email: Optional[str]
    status: str
    create_time: str


class MerchantListResponse(BaseModel):
    """商户列表响应"""
    total: int
    items: List[MerchantResponse]


@router.get("/merchants", response_model=MerchantListResponse)
async def get_merchants(
    name: Optional[str] = None,
    provider_id: Optional[str] = None,
    plan_type: Optional[str] = None,
    status: Optional[str] = None,
    time_range: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取商户列表（带筛选）"""
    merchants = [
        {
            "id": "M2026001",
            "name": "小明电商旗舰店",
            "logo": "",
            "provider_id": "1",
            "provider_name": "科技云",
            "plan_type": "premium",
            "plan_name": "高级版",
            "max_shops": 10,
            "shop_count": 5,
            "expire_date": "2027-03-31 23:59:59",
            "contact_name": "张小明",
            "contact_phone": "13800138001",
            "contact_email": "zhang@example.com",
            "status": "active",
            "create_time": "2026-01-15 10:30:00"
        },
        {
            "id": "M2026002",
            "name": "智慧零售体验店",
            "logo": "",
            "provider_id": "2",
            "provider_name": "智慧零售",
            "plan_type": "standard",
            "plan_name": "标准版",
            "max_shops": 5,
            "shop_count": 3,
            "expire_date": "2026-12-31 23:59:59",
            "contact_name": "李小红",
            "contact_phone": "13800138002",
            "contact_email": "li@example.com",
            "status": "active",
            "create_time": "2026-02-20 14:15:00"
        },
        {
            "id": "M2026003",
            "name": "未来电商专营店",
            "logo": "",
            "provider_id": "3",
            "provider_name": "未来电商",
            "plan_type": "ultimate",
            "plan_name": "旗舰版",
            "max_shops": 50,
            "shop_count": 12,
            "expire_date": "2027-06-30 23:59:59",
            "contact_name": "王大伟",
            "contact_phone": "13800138003",
            "contact_email": None,
            "status": "active",
            "create_time": "2026-03-01 09:00:00"
        },
        {
            "id": "M2026004",
            "name": "测试商户A",
            "logo": "",
            "provider_id": "1",
            "provider_name": "科技云",
            "plan_type": "free",
            "plan_name": "免费版",
            "max_shops": 1,
            "shop_count": 1,
            "expire_date": "2026-04-30 23:59:59",
            "contact_name": "赵测试",
            "contact_phone": "13800138004",
            "contact_email": None,
            "status": "pending",
            "create_time": "2026-04-10 16:45:00"
        },
        {
            "id": "M2026005",
            "name": "星辰科技商城",
            "logo": "",
            "provider_id": "1",
            "provider_name": "科技云",
            "plan_type": "basic",
            "plan_name": "普通版",
            "max_shops": 3,
            "shop_count": 3,
            "expire_date": "2026-03-15 23:59:59",
            "contact_name": "刘星辰",
            "contact_phone": "13800138005",
            "contact_email": None,
            "status": "expired",
            "create_time": "2025-06-20 11:20:00"
        },
        {
            "id": "M2026006",
            "name": "云端旗舰店",
            "logo": "",
            "provider_id": "2",
            "provider_name": "智慧零售",
            "plan_type": "custom",
            "plan_name": "定制版",
            "max_shops": 100,
            "shop_count": 25,
            "expire_date": "2028-01-31 23:59:59",
            "contact_name": "陈云端",
            "contact_phone": "13800138006",
            "contact_email": None,
            "status": "active",
            "create_time": "2025-12-01 08:30:00"
        }
    ]
    
    # 筛选逻辑
    if name:
        merchants = [m for m in merchants if name.lower() in m["name"].lower()]
    if provider_id:
        merchants = [m for m in merchants if m["provider_id"] == provider_id]
    if plan_type:
        merchants = [m for m in merchants if m["plan_type"] == plan_type]
    if status:
        merchants = [m for m in merchants if m["status"] == status]
    
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
            merchants = [m for m in merchants if datetime.strptime(m["create_time"], "%Y-%m-%d %H:%M:%S") >= start]
    
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        merchants = [m for m in merchants if start <= datetime.strptime(m["create_time"], "%Y-%m-%d %H:%M:%S") < end]
    
    total = len(merchants)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    merchants = merchants[start_idx:end_idx]
    
    return {
        "total": total,
        "items": merchants
    }


@router.get("/merchants/{merchant_id}")
async def get_merchant_detail(
    merchant_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取商户详情"""
    return {
        "id": merchant_id,
        "name": "示例商户",
        "status": "active"
    }


@router.post("/merchants/{merchant_id}/change-plan")
async def change_merchant_plan(
    merchant_id: str,
    plan_type: str,
    duration: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """变更商户套餐"""
    return {
        "success": True,
        "message": "套餐变更成功",
        "merchant_id": merchant_id,
        "new_plan": plan_type
    }


@router.post("/merchants/{merchant_id}/toggle-status")
async def toggle_merchant_status(
    merchant_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """切换商户状态"""
    return {
        "success": True,
        "message": "状态切换成功",
        "merchant_id": merchant_id
    }
