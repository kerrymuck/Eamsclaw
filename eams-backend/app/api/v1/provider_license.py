"""
服务商后台 - 授权码管理API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user

router = APIRouter()


class LicenseStats(BaseModel):
    """授权码统计"""
    total: int
    active: int
    pending: int
    expired: int


class LicenseResponse(BaseModel):
    """授权码响应"""
    id: str
    code: str
    merchant_name: Optional[str]
    merchant_id: Optional[str]
    shop_name: Optional[str]
    create_time: str
    expire_time: str
    status: str


class LicenseListResponse(BaseModel):
    """授权码列表响应"""
    total: int
    items: List[LicenseResponse]


class MerchantOption(BaseModel):
    """商户选项"""
    id: str
    name: str
    plan_name: str
    plan_type: str
    shop_count: int
    max_staff: int
    expire_date: str


@router.get("/stats", response_model=LicenseStats)
async def get_license_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取授权码统计"""
    return {
        "total": 12580,
        "active": 10234,
        "pending": 1560,
        "expired": 786
    }


@router.get("/price-info")
async def get_license_price_info(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取授权码价格信息"""
    return {
        "retail_price": 19.9,
        "level": "银牌服务商",
        "discount": 75,
        "purchase_price": 14.93
    }


@router.get("/merchants")
async def get_merchant_options(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> List[MerchantOption]:
    """获取商户选项（用于生成授权码）"""
    return [
        {
            "id": "M001",
            "name": "龙猫数码旗舰店",
            "plan_name": "专业版",
            "plan_type": "pro",
            "shop_count": 3,
            "max_staff": 10,
            "expire_date": "2027-04-10"
        },
        {
            "id": "M002",
            "name": "智慧零售体验店",
            "plan_name": "标准版",
            "plan_type": "standard",
            "shop_count": 2,
            "max_staff": 5,
            "expire_date": "2026-12-31"
        },
        {
            "id": "M003",
            "name": "未来电商专营店",
            "plan_name": "旗舰版",
            "plan_type": "ultimate",
            "shop_count": 5,
            "max_staff": 20,
            "expire_date": "2027-06-30"
        },
        {
            "id": "M004",
            "name": "星辰科技商城",
            "plan_name": "普通版",
            "plan_type": "basic",
            "shop_count": 1,
            "max_staff": 3,
            "expire_date": "2026-10-15"
        }
    ]


@router.get("/list", response_model=LicenseListResponse)
async def get_license_list(
    code: Optional[str] = None,
    status: Optional[str] = None,
    merchant_id: Optional[str] = None,
    time_range: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    date_range: Optional[List[str]] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取授权码列表"""
    licenses = [
        {
            "id": "1",
            "code": "EAMS-PRO-2026-4X8K9M2N",
            "merchant_name": "龙猫数码旗舰店",
            "merchant_id": "M001",
            "shop_name": "龙猫数码-主店",
            "create_time": "2026-04-10 14:30:00",
            "expire_time": "2027-04-10",
            "status": "active"
        },
        {
            "id": "2",
            "code": "EAMS-ENT-2026-7P3Q5R8T",
            "merchant_name": None,
            "merchant_id": None,
            "shop_name": None,
            "create_time": "2026-04-10 10:15:00",
            "expire_time": "2027-04-10",
            "status": "pending"
        },
        {
            "id": "3",
            "code": "EAMS-BAS-2026-2W6Y4U1I",
            "merchant_name": None,
            "merchant_id": None,
            "shop_name": None,
            "create_time": "2026-04-09 16:45:00",
            "expire_time": "2026-05-09",
            "status": "pending"
        },
        {
            "id": "4",
            "code": "EAMS-PRO-2026-9A1B2C3D",
            "merchant_name": "智慧零售体验店",
            "merchant_id": "M002",
            "shop_name": "智慧零售-总店",
            "create_time": "2026-04-08 09:20:00",
            "expire_time": "2026-12-31",
            "status": "active"
        },
        {
            "id": "5",
            "code": "EAMS-ULT-2026-5E6F7G8H",
            "merchant_name": "未来电商专营店",
            "merchant_id": "M003",
            "shop_name": "未来电商-旗舰店",
            "create_time": "2026-04-05 14:00:00",
            "expire_time": "2027-06-30",
            "status": "active"
        }
    ]
    
    # 筛选逻辑
    if code:
        licenses = [l for l in licenses if code.lower() in l["code"].lower()]
    if status:
        licenses = [l for l in licenses if l["status"] == status]
    if merchant_id:
        licenses = [l for l in licenses if l["merchant_id"] == merchant_id]
    
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
            licenses = [l for l in licenses if datetime.strptime(l["create_time"], "%Y-%m-%d %H:%M:%S") >= start]
    
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        licenses = [l for l in licenses if start <= datetime.strptime(l["create_time"], "%Y-%m-%d %H:%M:%S") < end]
    
    if date_range and len(date_range) == 2:
        start = datetime.strptime(date_range[0], "%Y-%m-%d")
        end = datetime.strptime(date_range[1], "%Y-%m-%d") + timedelta(days=1)
        licenses = [l for l in licenses if start <= datetime.strptime(l["create_time"], "%Y-%m-%d %H:%M:%S") < end]
    
    total = len(licenses)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    licenses = licenses[start_idx:end_idx]
    
    return {
        "total": total,
        "items": licenses
    }


@router.post("/generate")
async def generate_licenses(
    merchant_id: str,
    count: int,
    validity: int,
    remark: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """生成授权码"""
    return {
        "success": True,
        "message": f"成功生成 {count} 个授权码",
        "codes": [f"EAMS-GEN-{i:04d}" for i in range(count)]
    }


@router.post("/{license_id}/disable")
async def disable_license(
    license_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """禁用授权码"""
    return {
        "success": True,
        "message": "授权码已禁用",
        "license_id": license_id
    }


@router.get("/{license_id}/detail")
async def get_license_detail(
    license_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取授权码详情"""
    return {
        "id": license_id,
        "code": "EAMS-PRO-2026-4X8K9M2N",
        "status": "active"
    }
