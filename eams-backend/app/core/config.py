from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "EAMS"
    DEBUG: bool = False
    
    # 数据库
    DATABASE_URL: str = "postgresql://user:password@localhost/eams"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1天
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # AI配置
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    
    class Config:
        env_file = ".env"


settings = Settings()
