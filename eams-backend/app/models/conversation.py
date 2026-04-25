from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Boolean, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .user import Base
from app.core.db_types import UUID, ARRAY, JSON


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    platform_id = Column(UUID(as_uuid=True), ForeignKey("platforms.id"))
    platform_type = Column(String(20), nullable=False)
    platform_user_id = Column(String(100), nullable=False)
    platform_user_name = Column(String(100))
    platform_user_avatar = Column(Text)
    status = Column(String(20), default='active')  # active/closed/pending_handoff/handled
    priority = Column(Integer, default=0)
    tags = Column(ARRAY(String))
    meta_data = Column(JSON, default={})  # 避免使用保留字metadata
    last_message_at = Column(DateTime)
    last_message_preview = Column(String(200))
    unread_count = Column(Integer, default=0)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    handoff_reason = Column(String(50))
    handoff_note = Column(Text)
    handoff_at = Column(DateTime)
    closed_at = Column(DateTime)
    closed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    close_reason = Column(String(50))
    
    # 统计字段
    ai_message_count = Column(Integer, default=0)
    manual_message_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shop = relationship("Shop", back_populates="conversations")
    platform = relationship("Platform", back_populates="conversations")
    assigned_user = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")
    
    def __repr__(self):
        return f"<Conversation {self.id}:{self.status}>"


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    platform_msg_id = Column(String(100))
    direction = Column(String(10), nullable=False)  # in/out
    msg_type = Column(String(20), default='text')  # text/image/order/product/system
    content = Column(Text, nullable=False)
    content_html = Column(Text)
    attachments = Column(JSON, default=[])
    
    # AI相关
    intent = Column(String(50))
    intent_confidence = Column(DECIMAL(3, 2))
    reply_type = Column(String(20))  # ai/manual/template
    suggested_by_ai = Column(Boolean, default=False)
    
    # 发送者
    sender_type = Column(String(20))  # user/ai/agent/system
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    sender_name = Column(String(50))
    
    # 状态
    status = Column(String(20), default='sent')  # sending/sent/delivered/read/failed
    read_at = Column(DateTime)
    
    platform_created_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message {self.direction}:{self.content[:20]}...>"


class Handoff(Base):
    __tablename__ = "handoffs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False)
    reason = Column(String(50), nullable=False)
    note = Column(Text)
    triggered_by = Column(String(20))  # ai/user/system
    status = Column(String(20), default='pending')  # pending/accepted/resolved/timeout
    accepted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    accepted_at = Column(DateTime)
    resolved_at = Column(DateTime)
    resolution_note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Handoff {self.conversation_id}:{self.status}>"
