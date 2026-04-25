from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Enum, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class UserRole(enum.Enum):
    """用户角色"""
    SUPER_ADMIN = "super_admin"
    PROVIDER = "provider"
    MERCHANT = "merchant"


class UserStatus(enum.Enum):
    """用户状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"

    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20), unique=True, index=True)
    role = Column(Enum(UserRole), default=UserRole.MERCHANT)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    last_login_at = Column(DateTime)
    
    # 关联
    merchant = relationship("Merchant", back_populates="user", uselist=False)
    provider = relationship("Provider", back_populates="user", uselist=False)


class Merchant(BaseModel):
    """商户模型"""
    __tablename__ = "merchants"

    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    provider_id = Column(Integer, ForeignKey("providers.id"))
    name = Column(String(100), nullable=False)
    company_name = Column(String(200))
    business_license = Column(String(100))
    contact_name = Column(String(50))
    contact_phone = Column(String(20))
    contact_email = Column(String(100))
    address = Column(String(500))
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    
    # AI账户
    ai_balance = Column(DECIMAL(18, 4), default=0)
    ai_total_usage = Column(DECIMAL(18, 4), default=0)
    
    # 关联
    user = relationship("User", back_populates="merchant")
    provider = relationship("Provider", back_populates="merchants")
    ai_accounts = relationship("AIAccount", back_populates="merchant")


class Provider(BaseModel):
    """服务商模型"""
    __tablename__ = "providers"

    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    name = Column(String(100), nullable=False)
    company_name = Column(String(200))
    contact_name = Column(String(50))
    contact_phone = Column(String(20))
    contact_email = Column(String(100))
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    
    # 关联
    user = relationship("User", back_populates="provider")
    merchants = relationship("Merchant", back_populates="provider")
    packages = relationship("Package", back_populates="provider")
