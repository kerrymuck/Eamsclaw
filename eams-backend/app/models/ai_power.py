from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Boolean, DECIMAL, Numeric
from datetime import datetime
import uuid
from .user import Base
from app.core.db_types import UUID, JSON


class AIAccount(Base):
    """AI账户 - 商户AI算力账户余额管理"""
    __tablename__ = "ai_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False, unique=True)
    
    balance = Column(DECIMAL(10, 2), default=0)           # 可用余额
    frozen_amount = Column(DECIMAL(10, 2), default=0)     # 冻结金额
    total_recharged = Column(DECIMAL(10, 2), default=0)   # 累计充值
    total_consumed = Column(DECIMAL(10, 2), default=0)    # 累计消费
    free_quota = Column(DECIMAL(10, 2), default=20)       # 免费额度（新用户赠送）
    
    status = Column(String(20), default='active')         # active/frozen/suspended
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AITransaction(Base):
    """AI交易记录 - 充值/消费明细"""
    __tablename__ = "ai_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False)
    
    type = Column(String(20), nullable=False)             # recharge:充值 consumption:消费 refund:退款
    amount = Column(DECIMAL(10, 2), nullable=False)       # 金额（充值为正，消费为负）
    balance_after = Column(DECIMAL(10, 2), nullable=False) # 交易后余额
    
    description = Column(Text)                            # 交易描述
    reference_id = Column(UUID(as_uuid=True))             # 关联ID（订单ID或用量ID）
    reference_type = Column(String(20))                   # order/usage
    
    created_at = Column(DateTime, default=datetime.utcnow)


class AIUsage(Base):
    """AI用量记录 - 每次API调用的Token消耗明细"""
    __tablename__ = "ai_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # 服务商ID（如果有）
    
    model_name = Column(String(50), nullable=False)       # 模型名称
    model_provider = Column(String(20), nullable=False)   # 提供商
    
    input_tokens = Column(Integer, default=0)             # 输入Token数
    output_tokens = Column(Integer, default=0)            # 输出Token数
    total_tokens = Column(Integer, default=0)             # 总Token数
    
    input_cost = Column(DECIMAL(10, 4), default=0)        # 输入费用
    output_cost = Column(DECIMAL(10, 4), default=0)       # 输出费用
    total_cost = Column(DECIMAL(10, 4), default=0)        # 总费用
    
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    
    # 调用详情
    request_data = Column(JSON)                           # 请求数据（脱敏）
    response_time_ms = Column(Integer)                    # 响应时间（毫秒）
    status = Column(String(20), default='success')        # success/failed
    error_message = Column(Text)                          # 错误信息
    
    created_at = Column(DateTime, default=datetime.utcnow)


class AIModelPrice(Base):
    """AI模型价格配置 - 平台级价格设置"""
    __tablename__ = "ai_model_prices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    model_name = Column(String(50), nullable=False)       # 显示名称
    model_id = Column(String(50), nullable=False)         # API模型ID
    provider = Column(String(20), nullable=False)         # openai/anthropic/baidu/alibaba/zhipu/moonshot/bytedance
    
    # 官方零售价（商户看到的价格）
    official_input_price = Column(DECIMAL(10, 4), nullable=False)   # 输入价格/千token
    official_output_price = Column(DECIMAL(10, 4), nullable=False)  # 输出价格/千token
    
    # 服务商折扣（百分比）
    discount_normal = Column(Integer, default=100)        # 普通服务商
    discount_bronze = Column(Integer, default=85)         # 铜牌
    discount_silver = Column(Integer, default=75)         # 银牌
    discount_gold = Column(Integer, default=60)           # 金牌
    
    # 模型配置
    context_length = Column(Integer)                      # 上下文长度
    max_tokens = Column(Integer)                          # 最大输出token
    features = Column(JSON, default=[])                   # 特性标签
    icon = Column(String(10), default='🤖')              # 图标
    
    is_active = Column(Boolean, default=True)
    is_recommended = Column(Boolean, default=False)       # 是否推荐
    sort_order = Column(Integer, default=0)               # 排序
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RechargeOrder(Base):
    """充值订单"""
    __tablename__ = "recharge_orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False)
    
    order_no = Column(String(32), nullable=False, unique=True)  # 订单号
    amount = Column(DECIMAL(10, 2), nullable=False)             # 充值金额
    gift_amount = Column(DECIMAL(10, 2), default=0)             # 赠送金额
    
    payment_method = Column(String(20))                         # alipay/wechat/bank
    status = Column(String(20), default='pending')              # pending/paid/failed/closed
    
    paid_at = Column(DateTime)                                  # 支付时间
    transaction_no = Column(String(64))                         # 第三方支付流水号
    
    # 支付回调记录
    notify_data = Column(JSON)                                  # 回调数据
    notified_at = Column(DateTime)                              # 回调时间
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProviderSettlement(Base):
    """服务商结算记录"""
    __tablename__ = "provider_settlements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    period_start = Column(DateTime, nullable=False)         # 结算周期开始
    period_end = Column(DateTime, nullable=False)           # 结算周期结束
    
    total_usage = Column(DECIMAL(10, 4), default=0)         # 总用量金额
    platform_cost = Column(DECIMAL(10, 4), default=0)       # 平台成本
    provider_profit = Column(DECIMAL(10, 4), default=0)     # 服务商分润
    platform_profit = Column(DECIMAL(10, 4), default=0)     # 平台利润
    
    status = Column(String(20), default='pending')          # pending/settled
    settled_at = Column(DateTime)                           # 结算时间
    
    created_at = Column(DateTime, default=datetime.utcnow)
