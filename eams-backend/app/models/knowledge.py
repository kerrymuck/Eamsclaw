from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, ARRAY, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .user import Base


class KnowledgeCategory(Base):
    __tablename__ = "knowledge_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    platform_id = Column(UUID(as_uuid=True), ForeignKey("platforms.id"), nullable=True)  # 关联平台，null表示通用
    parent_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_categories.id"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shop = relationship("Shop")
    platform = relationship("Platform")
    parent = relationship("KnowledgeCategory", remote_side=[id])
    knowledges = relationship("Knowledge", back_populates="category")
    
    def __repr__(self):
        return f"<KnowledgeCategory {self.name}>"


class Knowledge(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    platform_id = Column(UUID(as_uuid=True), ForeignKey("platforms.id"), nullable=True)  # 关联平台，null表示通用
    category_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_categories.id"))
    question = Column(String(500), nullable=False)
    answer = Column(Text, nullable=False)
    answer_html = Column(Text)
    keywords = Column(ARRAY(String), default=[])
    similar_questions = Column(ARRAY(String), default=[])
    hit_count = Column(Integer, default=0)
    last_hit_at = Column(DateTime)
    status = Column(String(20), default='active')  # active/inactive/draft
    priority = Column(Integer, default=0)
    related_knowledge_ids = Column(ARRAY(UUID(as_uuid=True)))
    attachments = Column(JSON, default=[])
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shop = relationship("Shop")
    platform = relationship("Platform")
    category = relationship("KnowledgeCategory", back_populates="knowledges")
    
    def __repr__(self):
        return f"<Knowledge {self.question[:30]}...>"
