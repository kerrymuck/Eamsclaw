from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Enum, ForeignKey, DECIMAL
from app.models.base import BaseModel
import enum


class RechargeStatus(enum.Enum):
    """充值状态"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(enum.Enum):
    """支付方式"""
    WECHAT = "wechat"
    ALIPAY = "alipay"
    BANK_TRANSFER = "bank_transfer"


class RechargeRecord(BaseModel):
    """充值记录"""
    __tablename__ = "recharge_records"

    merchant_id = Column(Integer, ForeignKey("merchants.id"))
    
    # 订单信息
    order_no = Column(String(50), unique=True, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    
    # 支付信息
    payment_method = Column(Enum(PaymentMethod))
    payment_no = Column(String(100))  # 第三方支付流水号
    
    # 状态
    status = Column(Enum(RechargeStatus), default=RechargeStatus.PENDING)
    paid_at = Column(DateTime)
    
    # 备注
    remark = Column(String(500))


class FinancialRecord(BaseModel):
    """财务流水"""
    __tablename__ = "financial_records"

    merchant_id = Column(Integer, ForeignKey("merchants.id"))
    
    # 流水类型
    record_type = Column(String(20), nullable=False)  # recharge, consumption, refund
    
    # 金额
    amount = Column(DECIMAL(10, 2), nullable=False)
    balance_before = Column(DECIMAL(18, 4))
    balance_after = Column(DECIMAL(18, 4))
    
    # 关联信息
    related_id = Column(Integer)  # 关联的充值记录ID或消费记录ID
    related_type = Column(String(50))  # recharge, ai_usage
    
    # 描述
    description = Column(String(500))
