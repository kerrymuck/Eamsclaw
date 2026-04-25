"""
AI算力系统数据库迁移脚本
创建AI账户、交易记录、用量记录等表
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'ai_power_20240414'
down_revision = None  # 根据实际上一个迁移修改
branch_labels = None
depends_on = None


def upgrade():
    # 1. AI账户表
    op.create_table(
        'ai_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('shop_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('shops.id'), nullable=False, unique=True),
        sa.Column('balance', sa.DECIMAL(10, 2), default=0),
        sa.Column('frozen_amount', sa.DECIMAL(10, 2), default=0),
        sa.Column('total_recharged', sa.DECIMAL(10, 2), default=0),
        sa.Column('total_consumed', sa.DECIMAL(10, 2), default=0),
        sa.Column('free_quota', sa.DECIMAL(10, 2), default=20),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now())
    )
    op.create_index('idx_ai_accounts_shop_id', 'ai_accounts', ['shop_id'])
    
    # 2. AI交易记录表
    op.create_table(
        'ai_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('shop_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('shops.id'), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),  # recharge/consumption/refund
        sa.Column('amount', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('balance_after', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True)),
        sa.Column('reference_type', sa.String(20)),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now())
    )
    op.create_index('idx_ai_transactions_shop_id', 'ai_transactions', ['shop_id'])
    op.create_index('idx_ai_transactions_created_at', 'ai_transactions', ['created_at'])
    
    # 3. AI用量记录表
    op.create_table(
        'ai_usage',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('shop_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('shops.id'), nullable=False),
        sa.Column('provider_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('model_name', sa.String(50), nullable=False),
        sa.Column('model_provider', sa.String(20), nullable=False),
        sa.Column('input_tokens', sa.Integer, default=0),
        sa.Column('output_tokens', sa.Integer, default=0),
        sa.Column('total_tokens', sa.Integer, default=0),
        sa.Column('input_cost', sa.DECIMAL(10, 4), default=0),
        sa.Column('output_cost', sa.DECIMAL(10, 4), default=0),
        sa.Column('total_cost', sa.DECIMAL(10, 4), default=0),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id')),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('messages.id')),
        sa.Column('request_data', postgresql.JSONB()),
        sa.Column('response_time_ms', sa.Integer),
        sa.Column('status', sa.String(20), default='success'),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now())
    )
    op.create_index('idx_ai_usage_shop_id', 'ai_usage', ['shop_id'])
    op.create_index('idx_ai_usage_created_at', 'ai_usage', ['created_at'])
    op.create_index('idx_ai_usage_model', 'ai_usage', ['model_name'])
    
    # 4. AI模型价格配置表
    op.create_table(
        'ai_model_prices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('model_name', sa.String(50), nullable=False, unique=True),
        sa.Column('model_id', sa.String(50), nullable=False),
        sa.Column('provider', sa.String(20), nullable=False),
        sa.Column('official_input_price', sa.DECIMAL(10, 4), nullable=False),
        sa.Column('official_output_price', sa.DECIMAL(10, 4), nullable=False),
        sa.Column('discount_normal', sa.Integer, default=100),
        sa.Column('discount_bronze', sa.Integer, default=85),
        sa.Column('discount_silver', sa.Integer, default=75),
        sa.Column('discount_gold', sa.Integer, default=60),
        sa.Column('context_length', sa.Integer),
        sa.Column('max_tokens', sa.Integer),
        sa.Column('features', postgresql.JSONB(), default=[]),
        sa.Column('icon', sa.String(10), default='🤖'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_recommended', sa.Boolean, default=False),
        sa.Column('sort_order', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now())
    )
    op.create_index('idx_ai_model_prices_provider', 'ai_model_prices', ['provider'])
    op.create_index('idx_ai_model_prices_active', 'ai_model_prices', ['is_active'])
    
    # 5. 充值订单表
    op.create_table(
        'recharge_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('shop_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('shops.id'), nullable=False),
        sa.Column('order_no', sa.String(32), nullable=False, unique=True),
        sa.Column('amount', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('gift_amount', sa.DECIMAL(10, 2), default=0),
        sa.Column('payment_method', sa.String(20)),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('paid_at', sa.DateTime()),
        sa.Column('transaction_no', sa.String(64)),
        sa.Column('notify_data', postgresql.JSONB()),
        sa.Column('notified_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now())
    )
    op.create_index('idx_recharge_orders_shop_id', 'recharge_orders', ['shop_id'])
    op.create_index('idx_recharge_orders_status', 'recharge_orders', ['status'])
    op.create_index('idx_recharge_orders_order_no', 'recharge_orders', ['order_no'])
    
    # 6. 服务商结算表
    op.create_table(
        'provider_settlements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('provider_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('total_usage', sa.DECIMAL(10, 4), default=0),
        sa.Column('platform_cost', sa.DECIMAL(10, 4), default=0),
        sa.Column('provider_profit', sa.DECIMAL(10, 4), default=0),
        sa.Column('platform_profit', sa.DECIMAL(10, 4), default=0),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('settled_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now())
    )
    op.create_index('idx_provider_settlements_provider', 'provider_settlements', ['provider_id'])
    
    # 插入默认模型价格数据
    op.bulk_insert('ai_model_prices', [
        {
            'model_name': 'GPT-4',
            'model_id': 'gpt-4',
            'provider': 'openai',
            'official_input_price': 0.215,
            'official_output_price': 0.645,
            'context_length': 8192,
            'features': ['最强推理', '代码生成'],
            'icon': '🤖',
            'sort_order': 1
        },
        {
            'model_name': 'GPT-4o',
            'model_id': 'gpt-4o',
            'provider': 'openai',
            'official_input_price': 0.036,
            'official_output_price': 0.108,
            'context_length': 128000,
            'features': ['速度快', '多模态', '性价比高'],
            'icon': '⚡',
            'is_recommended': True,
            'sort_order': 2
        },
        {
            'model_name': 'Claude 3.5',
            'model_id': 'claude-3-5-sonnet-20241022',
            'provider': 'anthropic',
            'official_input_price': 0.108,
            'official_output_price': 0.538,
            'context_length': 200000,
            'features': ['长上下文', '安全', '创作'],
            'icon': '🧠',
            'sort_order': 3
        },
        {
            'model_name': 'Kimi K2.5',
            'model_id': 'kimi-k2.5',
            'provider': 'moonshot',
            'official_input_price': 0.012,
            'official_output_price': 0.024,
            'context_length': 256000,
            'features': ['长文本', '中文优化', '高性价比'],
            'icon': '🌙',
            'is_recommended': True,
            'sort_order': 4
        },
        {
            'model_name': '文心一言4.0',
            'model_id': 'ernie-bot-4',
            'provider': 'baidu',
            'official_input_price': 0.12,
            'official_output_price': 0.12,
            'context_length': 8000,
            'features': ['中文强', '搜索', '知识'],
            'icon': '🔴',
            'sort_order': 5
        },
        {
            'model_name': '通义千问Max',
            'model_id': 'qwen-max',
            'provider': 'alibaba',
            'official_input_price': 0.08,
            'official_output_price': 0.08,
            'context_length': 8000,
            'features': ['中文强', '代码', '推理'],
            'icon': '🟠',
            'sort_order': 6
        },
        {
            'model_name': '豆包Pro',
            'model_id': 'doubao-pro',
            'provider': 'bytedance',
            'official_input_price': 0.016,
            'official_output_price': 0.016,
            'context_length': 4000,
            'features': ['超低价', '中文', '年轻'],
            'icon': '🟢',
            'sort_order': 7
        },
        {
            'model_name': 'GLM-4',
            'model_id': 'glm-4',
            'provider': 'zhipu',
            'official_input_price': 0.10,
            'official_output_price': 0.10,
            'context_length': 128000,
            'features': ['国产', '开源', '多轮'],
            'icon': '🔵',
            'sort_order': 8
        }
    ])


def downgrade():
    op.drop_table('provider_settlements')
    op.drop_table('recharge_orders')
    op.drop_table('ai_model_prices')
    op.drop_table('ai_usage')
    op.drop_table('ai_transactions')
    op.drop_table('ai_accounts')
