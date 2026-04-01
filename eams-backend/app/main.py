from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.api.v1 import auth, dialog, knowledge, platform, analytics, upload, settings as settings_api
from app.tasks.scheduler import init_scheduler, start_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    print("🚀 EAMS服务启动中...")
    
    # 初始化定时任务
    init_scheduler()
    start_scheduler()
    
    yield
    
    # 关闭时执行
    shutdown_scheduler()
    print("👋 EAMS服务已关闭")


app = FastAPI(
    title="EAMS API",
    description="电商客服智能体系统API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(dialog.router, prefix="/api/v1/dialog", tags=["对话"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["知识库"])
app.include_router(platform.router, prefix="/api/v1/platform", tags=["平台对接"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["数据统计"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["文件上传"])
app.include_router(settings_api.router, prefix="/api/v1/settings", tags=["系统设置"])

# 静态文件服务（上传的文件）
upload_dir = os.path.join(os.getcwd(), "uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")


@app.get("/")
async def root():
    return {
        "name": "EAMS",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "认证管理",
            "对话管理",
            "知识库",
            "平台对接",
            "数据统计",
            "文件上传",
            "系统设置",
            "定时任务",
            "WebSocket"
        ]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
