"""
平台配置模型
管理各电商平台的API配置和授权信息
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Boolean, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .user import Base


class PlatformConfig(Base):
    """
    平台配置表
    存储各电商平台的API配置信息
    """
    __tablename__ = "platform_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_type = Column(String(20), nullable=False, unique=True)  # taobao/jd/pdd/douyin等
    
    # 平台基本信息
    platform_name = Column(String(50), nullable=False)
    platform_category = Column(String(20), default='domestic')  # domestic/crossborder
    description = Column(Text)
    icon_url = Column(Text)
    
    # API配置（加密存储）
    api_config = Column(JSON, default={})
    # {
    #     "app_key": "xxx",
    #     "app_secret": "xxx",  # 加密存储
    #     "api_base_url": "https://...",
    #     "auth_url": "https://...",
    #     "token_url": "https://...",
    #     "webhook_secret": "xxx"  # 用于验证webhook
    # }
    
    # OAuth配置
    oauth_config = Column(JSON, default={})
    # {
    #     "auth_type": "oauth2",
    #     "scopes": ["read", "write"],
    #     "callback_url": "https://your-app.com/callback",
    #     "token_expire_seconds": 86400
    # }
    
    # 功能配置
    features = Column(JSON, default={})
    # {
    #     "support_message": true,
    #     "support_order": true,
    #     "support_logistics": true,
    #     "support_product": true,
    #     "support_webhook": true
    # }
    
    # 状态
    is_enabled = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # 系统预设，不可删除
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PlatformConfig {self.platform_type}>"


class ShopPlatformAuth(Base):
    """
    店铺平台授权表
    存储每个店铺在各平台的授权信息
    """
    __tablename__ = "shop_platform_auths"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    platform_config_id = Column(UUID(as_uuid=True), ForeignKey("platform_configs.id", ondelete="CASCADE"), nullable=False)
    
    # 平台店铺信息
    platform_shop_id = Column(String(100), nullable=False)  # 平台侧的店铺ID
    platform_shop_name = Column(String(100))
    platform_shop_logo = Column(Text)
    
    # 授权状态
    auth_status = Column(String(20), default='pending')  # pending/authorized/expired/revoked/error
    auth_error = Column(Text)  # 授权错误信息
    
    # 授权凭证（加密存储）
    auth_credentials = Column(JSON, default={})
    # {
    #     "access_token": "xxx",  # 加密
    #     "refresh_token": "xxx",  # 加密
    #     "token_type": "Bearer",
    #     "expires_at": "2024-01-01T00:00:00"
    # }
    
    # 授权详情
    authorized_at = Column(DateTime)
    expires_at = Column(DateTime)
    refreshed_at = Column(DateTime)
    refresh_count = Column(Integer, default=0)
    
    # Webhook配置
    webhook_config = Column(JSON, default={})
    # {
    #     "webhook_url": "https://...",
    #     "webhook_secret": "xxx",
    #     "subscribed_events": ["message", "order"]
    # }
    
    # 同步配置
    sync_config = Column(JSON, default={})
    # {
    #     "auto_sync_messages": true,
    #     "auto_sync_orders": true,
    #     "sync_interval_minutes": 5
    # }
    
    # 统计数据
    stats = Column(JSON, default={})
    # {
    #     "last_sync_at": "2024-01-01T00:00:00",
    #     "total_messages": 100,
    #     "total_orders": 50
    # }
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('shop_id', 'platform_config_id', 'platform_shop_id'),)
    
    # Relationships
    shop = relationship("Shop")
    platform_config = relationship("PlatformConfig")
    
    def __repr__(self):
        return f"<ShopPlatformAuth {self.shop_id}:{self.platform_config_id}>"


class PlatformWebhookLog(Base):
    """
    平台Webhook日志
    记录各平台推送的消息
    """
    __tablename__ = "platform_webhook_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_platform_auth_id = Column(UUID(as_uuid=True), ForeignKey("shop_platform_auths.id", ondelete="CASCADE"), nullable=False)
    
    # Webhook信息
    event_type = Column(String(50), nullable=False)  # message/order/logistics等
    event_id = Column(String(100))  # 平台事件ID
    payload = Column(JSON)  # 原始payload
    
    # 处理状态
    status = Column(String(20), default='pending')  # pending/processing/success/failed
    processed_at = Column(DateTime)
    error_message = Column(Text)
    
    # 签名验证
    signature = Column(String(255))
    signature_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    shop_platform_auth = relationship("ShopPlatformAuth")
    
    def __repr__(self):
        return f"<PlatformWebhookLog {self.event_type}:{self.event_id}>"
