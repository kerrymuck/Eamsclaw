from sqlalchemy import Column, String, DateTime, ForeignKey, Text, UniqueConstraint
from datetime import datetime
import uuid
from .user import Base
from app.core.db_types import UUID, INET, JSON


class Setting(Base):
    __tablename__ = "settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"))
    
    setting_key = Column(String(100), nullable=False)
    setting_value = Column(Text)
    value_type = Column(String(20), default='string')  # string/number/boolean/json
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('shop_id', 'setting_key'),)
    
    def __repr__(self):
        return f"<Setting {self.setting_key}>"


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    action = Column(String(50), nullable=False)  # create/update/delete/login/logout
    resource_type = Column(String(50))  # conversation/knowledge/user/settings
    resource_id = Column(UUID(as_uuid=True))
    
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(INET)
    user_agent = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AuditLog {self.action}:{self.resource_type}>"
