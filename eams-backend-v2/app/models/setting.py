from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Enum
from app.models.base import BaseModel
import enum


class SettingGroup(enum.Enum):
    """设置分组"""
    GENERAL = "general"
    WECHAT = "wechat"
    PAYMENT = "payment"
    SMS = "sms"
    AI = "ai"


class SettingType(enum.Enum):
    """设置值类型"""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    JSON = "json"


class SystemSetting(BaseModel):
    """系统设置"""
    __tablename__ = "system_settings"

    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text)
    group = Column(Enum(SettingGroup), default=SettingGroup.GENERAL)
    type = Column(Enum(SettingType), default=SettingType.STRING)
    description = Column(String(500))
    is_encrypted = Column(Boolean, default=False)  # 是否加密存储
    is_editable = Column(Boolean, default=True)  # 是否可编辑
    sort_order = Column(Integer, default=0)
