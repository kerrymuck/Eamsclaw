"""
系统设置模型
存储微信公众号、支付接口、短信等配置
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base
import uuid


class SystemSetting(Base):
    """系统设置表 - 键值对存储"""
    __tablename__ = "system_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    setting_key = Column(String(100), unique=True, nullable=False, index=True)
    setting_value = Column(Text, nullable=True)
    setting_group = Column(String(50), nullable=False, default='general')  # wechat, payment, sms, general
    description = Column(String(255), nullable=True)
    is_encrypted = Column(Boolean, default=False)  # 是否加密存储（如密钥）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.setting_key,
            'value': self.setting_value,
            'group': self.setting_group,
            'description': self.description,
            'is_encrypted': self.is_encrypted,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }