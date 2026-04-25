"""
超管后台 - 财务管理API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user

router = APIRouter()


class RechargeRecord(BaseModel):
    """充值记录"""
    id: str
    order_no: str
    create_time: str
    provider_name: str
    provider_id: str
    amount: float
    payment_method: str
    status: str
    remark: Optional[str] = None


class RechargeListResponse(BaseModel):
    """充值列表响应"""
    total: int
    items: List[RechargeRecord]


@router.get("/finance/recharge", response_model=RechargeListResponse)
async def get_recharge_list(
    order_no: Optional[str] = None,
    provider_id: Optional[str] = None,
    payment_method: Optional[str] = None,
    status: Optional[str] = None,
    time_range: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取充值明细列表（带筛选）"""
    records = [
        {
            "id": "1",
            "order_no": "RC202603310001",
            "create_time": "2026-03-31 14:30:25",
            "provider_name": "科技云",
            "provider_id": "1",
            "amount": 50000,
            "payment_method": "银行转账",
            "status": "success",
            "remark": "季度充值"
        },
        {
            "id": "2",
            "order_no": "RC202603310002",
            "create_time": "2026-03-31 11:15:10",
            "provider_name": "智慧零售",
            "provider_id": "2",
            "amount": 20000,
            "payment_method": "支付宝",
            "status": "success",
            "remark": ""
        },
        {
            "id": "3",
            "order_no": "RC202603310003",
            "create_time": "2026-03-31 09:45:33",
            "provider_name": "未来电商",
            "provider_id": "3",
            "amount": 10000,
            "payment_method": "微信支付",
            "status": "pending",
            "remark": "待确认"
        },
        {
            "id": "4",
            "order_no": "RC202603300001",
            "create_time": "2026-03-30 16:20:15",
            "provider_name": "星辰科技",
            "provider_id": "4",
            "amount": 30000,
            "payment_method": "银行转账",
            "status": "success",
            "remark": ""
        },
        {
            "id": "5",
            "order_no": "RC202603290001",
            "create_time": "2026-03-29 10:30:00",
            "provider_name": "云端商务",
            "provider_id": "5",
            "amount": 15000,
            "payment_method": "支付宝",
            "status": "failed",
            "remark": "支付超时"
        }
    ]
    
    # 筛选逻辑
    if order_no:
        records = [r for r in records if order_no.lower() in r["order_no"].lower()]
    if provider_id:
        records = [r for r in records if r["provider_id"] == provider_id]
    if payment_method:
        records = [r for r in records if r["payment_method"] == payment_method]
    if status:
        records = [r for r in records if r["status"] == status]
    if min_amount is not None:
        records = [r for r in records if r["amount"] >= min_amount]
    if max_amount is not None:
        records = [r for r in records if r["amount"] <= max_amount]
    
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
            records = [r for r in records if datetime.strptime(r["create_time"], "%Y-%m-%d %H:%M:%S") >= start]
    
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        records = [r for r in records if start <= datetime.strptime(r["create_time"], "%Y-%m-%d %H:%M:%S") < end]
    
    total = len(records)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    records = records[start_idx:end_idx]
    
    return {
        "total": total,
        "items": records
    }


@router.get("/finance/recharge/export")
async def export_recharge(
    order_no: Optional[str] = None,
    provider_id: Optional[str] = None,
    payment_method: Optional[str] = None,
    status: Optional[str] = None,
    time_range: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """导出充值明细"""
    return {
        "success": True,
        "message": "导出成功",
        "download_url": "/api/v1/admin/finance/recharge/export/download"
    }
