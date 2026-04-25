"""
服务商后台 - 商户管理API
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
    contact_name: str
    contact_phone: str
    email: Optional[str]
    plan_type: str
    plan_name: str
    package_name: str
    yearly_price: int
    max_shops: int
    shop_count: int
    staff_count: int
    license_count: int
    expire_date: str
    remaining_days: int
    status: str
    create_time: str


class MerchantListResponse(BaseModel):
    """商户列表响应"""
    total: int
    items: List[MerchantResponse]


class MerchantStats(BaseModel):
    """商户统计"""
    total: int
    active: int
    expiring: int
    expired: int


@router.get("/stats", response_model=MerchantStats)
async def get_merchant_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取商户统计"""
    return {
        "total": 328,
        "active": 286,
        "expiring": 42,
        "expired": 15
    }


@router.get("/list", response_model=MerchantListResponse)
async def get_merchant_list(
    name: Optional[str] = None,
    status: Optional[str] = None,
    plan_type: Optional[str] = None,
    time_range: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    date_range: Optional[List[str]] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取服务商旗下的商户列表"""
    merchants = [
        {
            "id": "1",
            "name": "龙猫数码旗舰店",
            "logo": "",
            "contact_name": "张三",
            "contact_phone": "13800138001",
            "email": "zhangsan@example.com",
            "plan_type": "premium",
            "plan_name": "高级版",
            "package_name": "高级版",
            "yearly_price": 1299,
            "max_shops": 10,
            "shop_count": 5,
            "staff_count": 12,
            "license_count": 10,
            "expire_date": "2026-12-31",
            "remaining_days": 265,
            "status": "active",
            "create_time": "2024-01-15"
        },
        {
            "id": "2",
            "name": "潮流服饰专营店",
            "logo": "",
            "contact_name": "李四",
            "contact_phone": "13800138002",
            "email": "lisi@example.com",
            "plan_type": "standard",
            "plan_name": "标准版",
            "package_name": "标准版",
            "yearly_price": 599,
            "max_shops": 3,
            "shop_count": 3,
            "staff_count": 8,
            "license_count": 3,
            "expire_date": "2026-11-30",
            "remaining_days": 235,
            "status": "active",
            "create_time": "2024-02-20"
        },
        {
            "id": "3",
            "name": "美妆护肤集合店",
            "logo": "",
            "contact_name": "王五",
            "contact_phone": "13800138003",
            "email": "wangwu@example.com",
            "plan_type": "ultimate",
            "plan_name": "旗舰版",
            "package_name": "旗舰版",
            "yearly_price": 2999,
            "max_shops": 50,
            "shop_count": 12,
            "staff_count": 25,
            "license_count": 50,
            "expire_date": "2025-04-15",
            "remaining_days": 5,
            "status": "expiring",
            "create_time": "2024-03-10"
        },
        {
            "id": "4",
            "name": "小明个人工作室",
            "logo": "",
            "contact_name": "赵小明",
            "contact_phone": "13800138004",
            "email": "zhao@example.com",
            "plan_type": "free",
            "plan_name": "免费版",
            "package_name": "免费版",
            "yearly_price": 0,
            "max_shops": 1,
            "shop_count": 1,
            "staff_count": 2,
            "license_count": 1,
            "expire_date": "2026-06-30",
            "remaining_days": 75,
            "status": "active",
            "create_time": "2024-04-01"
        },
        {
            "id": "5",
            "name": "未来科技有限公司",
            "logo": "",
            "contact_name": "钱总",
            "contact_phone": "13800138005",
            "email": "qian@example.com",
            "plan_type": "custom",
            "plan_name": "定制版",
            "package_name": "定制版",
            "yearly_price": 5998,
            "max_shops": 100,
            "shop_count": 68,
            "staff_count": 150,
            "license_count": 100,
            "expire_date": "2027-03-31",
            "remaining_days": 350,
            "status": "active",
            "create_time": "2024-01-10"
        }
    ]
    
    # 筛选逻辑
    if name:
        merchants = [m for m in merchants if name.lower() in m["name"].lower()]
    if status:
        merchants = [m for m in merchants if m["status"] == status]
    if plan_type:
        merchants = [m for m in merchants if m["plan_type"] == plan_type]
    
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
            merchants = [m for m in merchants if datetime.strptime(m["create_time"], "%Y-%m-%d") >= start]
    
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        merchants = [m for m in merchants if start <= datetime.strptime(m["create_time"], "%Y-%m-%d") < end]
    
    if date_range and len(date_range) == 2:
        start = datetime.strptime(date_range[0], "%Y-%m-%d")
        end = datetime.strptime(date_range[1], "%Y-%m-%d") + timedelta(days=1)
        merchants = [m for m in merchants if start <= datetime.strptime(m["expire_date"], "%Y-%m-%d") < end]
    
    total = len(merchants)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    merchants = merchants[start_idx:end_idx]
    
    return {
        "total": total,
        "items": merchants
    }


@router.get("/{merchant_id}")
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


@router.post("/{merchant_id}/renew")
async def renew_merchant(
    merchant_id: str,
    months: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """商户续费"""
    return {
        "success": True,
        "message": f"续费 {months} 个月成功",
        "merchant_id": merchant_id
    }


@router.post("/{merchant_id}/upgrade")
async def upgrade_merchant_plan(
    merchant_id: str,
    new_plan_type: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """升级商户套餐"""
    return {
        "success": True,
        "message": "套餐升级成功",
        "merchant_id": merchant_id,
        "new_plan": new_plan_type
    }


@router.post("/{merchant_id}/toggle-status")
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
