from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, JSON, Boolean, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .user import Base


class IntentLog(Base):
    __tablename__ = "intent_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False)
    
    input_text = Column(Text, nullable=False)
    intent = Column(String(50))
    confidence = Column(DECIMAL(3, 2))
    alternatives = Column(JSON, default=[])
    
    model_name = Column(String(50))
    model_version = Column(String(20))
    processing_time = Column(Integer)  # milliseconds
    
    is_correct = Column(Boolean)
    corrected_intent = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<IntentLog {self.intent}:{self.confidence}>"


class ModelConfig(Base):
    __tablename__ = "model_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"))
    
    config_name = Column(String(50), nullable=False)
    config_type = Column(String(20), nullable=False)  # intent/reply/routing
    
    model_provider = Column(String(20))  # openai/anthropic/local
    model_name = Column(String(50))
    api_key_encrypted = Column(Text)
    api_endpoint = Column(Text)
    
    temperature = Column(DECIMAL(3, 2), default=0.7)
    max_tokens = Column(Integer, default=150)
    top_p = Column(DECIMAL(3, 2), default=1.0)
    
    system_prompt = Column(Text)
    prompt_template = Column(Text)
    
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ModelConfig {self.config_name}>"
