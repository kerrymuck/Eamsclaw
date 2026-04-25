"""
数据库模块别名
兼容旧代码导入
"""
from app.core.database import (
    engine,
    AsyncSessionLocal,
    Base,
    get_db
)
from sqlalchemy.orm import sessionmaker, Session

# 同步SessionLocal（用于AI算力服务）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

__all__ = ["engine", "AsyncSessionLocal", "Base", "get_db", "SessionLocal"]
