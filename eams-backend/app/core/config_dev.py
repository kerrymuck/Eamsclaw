# EAMS 本地开发环境配置 (SQLite版本)
# 用于快速测试，生产环境请使用PostgreSQL

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "EAMS"
    DEBUG: bool = True
    
    # 数据库 - 开发环境使用SQLite
    DATABASE_URL: str = "sqlite+aiosqlite:///./eams_dev.db"
    
    # Redis - 开发环境可禁用
    REDIS_URL: str = ""
    
    # RabbitMQ - 开发环境可禁用
    RABBITMQ_URL: str = ""
    
    # 安全配置
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1天
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # AI配置
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    class Config:
        env_file = ".env"


settings = Settings()
