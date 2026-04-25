from pydantic_settings import BaseSettings
from typing import List, Optional


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
    MOONSHOT_API_KEY: str = ""
    
    # 支付宝配置
    ALIPAY_APP_ID: str = ""
    ALIPAY_PRIVATE_KEY: str = ""
    ALIPAY_PUBLIC_KEY: str = ""
    ALIPAY_GATEWAY: str = "https://openapi.alipay.com/gateway.do"
    ALIPAY_NOTIFY_URL: str = ""
    
    # 微信支付配置
    WECHAT_MCH_ID: str = ""
    WECHAT_API_KEY: str = ""
    WECHAT_CERT_PATH: str = ""
    WECHAT_KEY_PATH: str = ""
    WECHAT_NOTIFY_URL: str = ""
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10485760
    UPLOAD_DIR: str = "uploads"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/eams.log"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # 忽略额外的环境变量


settings = Settings()
