"""
服务商后台 - 财务管理API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user

router = APIRouter()


class FinanceStats(BaseModel):
    """财务统计"""
    total_revenue: str
    month_revenue: str
    balance: str


class BillRecord(BaseModel):
    """账单记录"""
    id: str
    date: str
    order_no: str
    type: str
    description: str
    amount: str
    status: str


class BillListResponse(BaseModel):
    """账单列表响应"""
    total: int
    items: List[BillRecord]


@router.get("/stats", response_model=FinanceStats)
async def get_finance_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取财务统计"""
    return {
        "total_revenue": "1,286,500",
        "month_revenue": "86,500",
        "balance": "125,800"
    }


@router.get("/bills", response_model=BillListResponse)
async def get_bill_list(
    order_no: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    time_range: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    bill_type: Optional[str] = Query(None, alias="billType"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取账单明细列表"""
    bills = [
        {
            "id": "1",
            "date": "2026-04-10 14:30:00",
            "order_no": "RE202604100001",
            "type": "income",
            "description": "商户「龙猫数码」续费",
            "amount": "4,999",
            "status": "completed"
        },
        {
            "id": "2",
            "date": "2026-04-10 10:15:00",
            "order_no": "AI202604100002",
            "type": "expense",
            "description": "AI算力充值",
            "amount": "10,000",
            "status": "completed"
        },
        {
            "id": "3",
            "date": "2026-04-09 16:45:00",
            "order_no": "RE202604090003",
            "type": "income",
            "description": "商户「潮流服饰」购买授权",
            "amount": "1,999",
            "status": "completed"
        },
        {
            "id": "4",
            "date": "2026-04-09 09:20:00",
            "order_no": "LC202604090004",
            "type": "expense",
            "description": "购买授权码",
            "amount": "5,000",
            "status": "completed"
        },
        {
            "id": "5",
            "date": "2026-04-08 14:00:00",
            "order_no": "RE202604080005",
            "type": "income",
            "description": "商户「美妆护肤」续费",
            "amount": "2,999",
            "status": "pending"
        }
    ]
    
    # 筛选逻辑
    if order_no:
        bills = [b for b in bills if order_no.lower() in b["order_no"].lower()]
    if type:
        bills = [b for b in bills if b["type"] == type]
    if status:
        bills = [b for b in bills if b["status"] == status]
    if bill_type and bill_type != "all":
        bills = [b for b in bills if b["type"] == bill_type]
    
    # 金额筛选（简化处理，实际应解析金额字符串）
    if min_amount is not None:
        bills = [b for b in bills if float(b["amount"].replace(",", "")) >= min_amount]
    if max_amount is not None:
        bills = [b for b in bills if float(b["amount"].replace(",", "")) <= max_amount]
    
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
            bills = [b for b in bills if datetime.strptime(b["date"], "%Y-%m-%d %H:%M:%S") >= start]
    
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        bills = [b for b in bills if start <= datetime.strptime(b["date"], "%Y-%m-%d %H:%M:%S") < end]
    
    total = len(bills)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    bills = bills[start_idx:end_idx]
    
    return {
        "total": total,
        "items": bills
    }


@router.post("/recharge")
async def create_recharge(
    amount: float,
    payment: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建充值订单"""
    return {
        "success": True,
        "message": "充值订单已创建",
        "order_no": f"RC{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "amount": amount,
        "payment": payment
    }
