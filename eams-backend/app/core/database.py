from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

# 数据库URL处理
database_url = settings.DATABASE_URL

# 根据数据库类型创建引擎
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        future=True
    )
    # 创建异步会话工厂
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async def get_db():
        """获取数据库会话（异步）"""
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

elif database_url.startswith("sqlite://"):
    # SQLite使用同步引擎
    engine = create_engine(
        database_url.replace("sqlite://", "sqlite:///").replace("sqlite:////", "sqlite:///"),
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False}
    )
    # 创建同步会话工厂
    AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def get_db():
        """获取数据库会话（同步）"""
        db = AsyncSessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
else:
    raise ValueError(f"不支持的数据库类型: {database_url}")

Base = declarative_base()
