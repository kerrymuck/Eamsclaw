from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text, ARRAY, JSON, DECIMAL, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    real_name = Column(String(50))
    avatar_url = Column(Text)
    role = Column(String(20), default='customer_service')
    status = Column(String(20), default='active')
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owned_shops = relationship("Shop", back_populates="owner")
    shop_memberships = relationship("ShopMember", back_populates="user")
    assigned_conversations = relationship("Conversation", back_populates="assigned_user")
    
    def __repr__(self):
        return f"<User {self.username}>"


class Shop(Base):
    __tablename__ = "shops"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(String(20), default='active')
    settings = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="owned_shops")
    members = relationship("ShopMember", back_populates="shop")
    platforms = relationship("Platform", back_populates="shop")
    conversations = relationship("Conversation", back_populates="shop")
    
    def __repr__(self):
        return f"<Shop {self.name}>"


class ShopMember(Base):
    __tablename__ = "shop_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), default='member')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('shop_id', 'user_id'),)
    
    # Relationships
    shop = relationship("Shop", back_populates="members")
    user = relationship("User", back_populates="shop_memberships")
    
    def __repr__(self):
        return f"<ShopMember {self.user_id}@{self.shop_id}>"


class Platform(Base):
    __tablename__ = "platforms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    platform_type = Column(String(20), nullable=False)  # taobao/jd/pdd
    platform_shop_id = Column(String(100), nullable=False)
    platform_shop_name = Column(String(100))
    auth_status = Column(String(20), default='pending')
    auth_data = Column(JSON, default={})
    settings = Column(JSON, default={})
    last_auth_at = Column(DateTime)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('shop_id', 'platform_type'),)
    
    # Relationships
    shop = relationship("Shop", back_populates="platforms")
    conversations = relationship("Conversation", back_populates="platform")
    
    def __repr__(self):
        return f"<Platform {self.platform_type}:{self.platform_shop_name}>"
