from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db
from app.cache import close_redis
from app.middlewares.cors import setup_cors
from app.middlewares.error_handler import exception_handler, global_exception_handler
from app.exceptions import BaseException
from app.api.v1 import router as api_v1_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    await init_db()
    print("✅ 数据库初始化完成")
    yield
    # 关闭时
    await close_redis()
    print("👋 应用已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="EAMS 后端API",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # 配置CORS
    setup_cors(app)
    
    # 注册异常处理器
    app.add_exception_handler(BaseException, exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
    
    # 注册路由
    app.include_router(api_v1_router, prefix="/api/v1")
    
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app


app = create_app()
