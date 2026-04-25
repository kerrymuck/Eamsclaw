from sqlalchemy import Column, DateTime, Integer, ForeignKey, String, DECIMAL, UniqueConstraint
from datetime import datetime
import uuid
from .user import Base
from app.core.db_types import UUID


class DailyStats(Base):
    __tablename__ = "daily_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    stat_date = Column(DateTime, nullable=False)
    
    # 对话统计
    total_conversations = Column(Integer, default=0)
    new_conversations = Column(Integer, default=0)
    closed_conversations = Column(Integer, default=0)
    active_conversations = Column(Integer, default=0)
    
    # 消息统计
    total_messages = Column(Integer, default=0)
    user_messages = Column(Integer, default=0)
    ai_messages = Column(Integer, default=0)
    manual_messages = Column(Integer, default=0)
    
    # 响应时间
    avg_response_time = Column(Integer, default=0)
    max_response_time = Column(Integer, default=0)
    min_response_time = Column(Integer, default=0)
    
    # 转人工
    handoff_count = Column(Integer, default=0)
    handoff_rate = Column(DECIMAL(5, 2), default=0)
    avg_handoff_time = Column(Integer, default=0)
    
    # AI统计
    ai_reply_count = Column(Integer, default=0)
    ai_accuracy = Column(DECIMAL(5, 2), default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('shop_id', 'stat_date'),)
    
    def __repr__(self):
        return f"<DailyStats {self.shop_id}:{self.stat_date}>"


class HourlyStats(Base):
    __tablename__ = "hourly_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    stat_date = Column(DateTime, nullable=False)
    stat_hour = Column(Integer, nullable=False)
    
    conversation_count = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    avg_response_time = Column(Integer, default=0)
    handoff_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('shop_id', 'stat_date', 'stat_hour'),)
    
    def __repr__(self):
        return f"<HourlyStats {self.shop_id}:{self.stat_date}H{self.stat_hour}>"


class IntentStats(Base):
    __tablename__ = "intent_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    stat_date = Column(DateTime, nullable=False)
    intent = Column(String(50), nullable=False)
    count = Column(Integer, default=0)
    avg_confidence = Column(DECIMAL(3, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('shop_id', 'stat_date', 'intent'),)
    
    def __repr__(self):
        return f"<IntentStats {self.intent}:{self.count}>"
