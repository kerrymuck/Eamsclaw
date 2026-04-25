from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Enum, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class PackageType(enum.Enum):
    """套餐类型"""
    BASIC = "basic"          # 基础版
    STANDARD = "standard"    # 标准版
    PREMIUM = "premium"      # 高级版
    ENTERPRISE = "enterprise" # 企业版


class PackageStatus(enum.Enum):
    """套餐状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SOLD_OUT = "sold_out"


class Package(BaseModel):
    """套餐模型"""
    __tablename__ = "packages"

    provider_id = Column(Integer, ForeignKey("providers.id"))
    name = Column(String(100), nullable=False)
    type = Column(Enum(PackageType), default=PackageType.BASIC)
    description = Column(Text)
    
    # 价格
    price = Column(DECIMAL(10, 2), nullable=False)
    original_price = Column(DECIMAL(10, 2))
    
    # AI额度
    ai_tokens = Column(Integer, default=0)  # 包含的Token数量
    ai_calls = Column(Integer, default=0)   # 包含的调用次数
    
    # 有效期
    validity_days = Column(Integer, default=30)  # 有效期（天）
    
    # 状态
    status = Column(Enum(PackageStatus), default=PackageStatus.ACTIVE)
    sort_order = Column(Integer, default=0)
    
    # 关联
    provider = relationship("Provider", back_populates="packages")


class MerchantPackage(BaseModel):
    """商户套餐订阅记录"""
    __tablename__ = "merchant_packages"

    merchant_id = Column(Integer, ForeignKey("merchants.id"))
    package_id = Column(Integer, ForeignKey("packages.id"))
    
    # 订阅信息
    subscribed_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # 使用情况
    tokens_used = Column(Integer, default=0)
    calls_used = Column(Integer, default=0)
    
    # 支付信息
    amount_paid = Column(DECIMAL(10, 2))
    payment_status = Column(String(20), default="pending")  # pending, paid, refunded
    
    # 状态
    is_active = Column(Boolean, default=True)
