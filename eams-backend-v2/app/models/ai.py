from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Enum, ForeignKey, DECIMAL
from app.models.base import BaseModel
import enum


class AIProvider(enum.Enum):
    """AI服务商"""
    MOONSHOT = "moonshot"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"
    DASHSCOPE = "dashscope"
    DOUBAO = "doubao"
    YI = "yi"


class AIModelStatus(enum.Enum):
    """AI模型状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class AIAccount(BaseModel):
    """AI账户模型"""
    __tablename__ = "ai_accounts"

    merchant_id = Column(Integer, ForeignKey("merchants.id"))
    provider = Column(Enum(AIProvider), nullable=False)
    
    # API密钥（加密存储）
    api_key_encrypted = Column(Text)
    
    # 模型配置
    default_model = Column(String(50))
    
    # 使用限制
    daily_limit = Column(Integer, default=1000)
    monthly_limit = Column(Integer, default=10000)
    
    # 状态
    status = Column(Enum(AIModelStatus), default=AIModelStatus.ACTIVE)


class AIModel(BaseModel):
    """AI模型配置"""
    __tablename__ = "ai_models"

    provider = Column(Enum(AIProvider), nullable=False)
    model_id = Column(String(50), nullable=False)  # 如: gpt-4, kimi-k2.5
    model_name = Column(String(100), nullable=False)  # 显示名称
    
    # 定价
    input_price = Column(DECIMAL(10, 6), default=0)  # 每1K tokens输入价格
    output_price = Column(DECIMAL(10, 6), default=0)  # 每1K tokens输出价格
    
    # 性能指标
    max_tokens = Column(Integer, default=4096)
    response_time = Column(Integer)  # 平均响应时间(ms)
    accuracy = Column(Integer)  # 准确率(%)
    star_rating = Column(Integer)  # 星级评分(1-5)
    
    # 状态
    status = Column(Enum(AIModelStatus), default=AIModelStatus.ACTIVE)
    sort_order = Column(Integer, default=0)


class AIUsageRecord(BaseModel):
    """AI使用记录"""
    __tablename__ = "ai_usage_records"

    merchant_id = Column(Integer, ForeignKey("merchants.id"))
    model_id = Column(String(50), nullable=False)
    
    # 使用详情
    request_tokens = Column(Integer, default=0)
    response_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # 费用
    cost = Column(DECIMAL(18, 6), default=0)
    
    # 请求信息
    request_id = Column(String(100))
    status = Column(String(20))  # success, failed
    error_message = Column(Text)
