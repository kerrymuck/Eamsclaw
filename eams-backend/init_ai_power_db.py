"""
直接创建AI算力相关数据库表（不使用alembic）
"""

import sys
sys.path.insert(0, 'E:\\EAMS-Project\\eams-backend')

from sqlalchemy import create_engine, text
from app.core.config import settings

def create_tables():
    # 使用SQLite
    engine = create_engine('sqlite:///E:\\EAMS-Project\\eams-backend\\eams_dev.db')
    
    with engine.connect() as conn:
        # 1. AI账户表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ai_accounts (
                id VARCHAR(36) PRIMARY KEY,
                shop_id VARCHAR(36) NOT NULL UNIQUE,
                balance DECIMAL(10,2) DEFAULT 0,
                frozen_amount DECIMAL(10,2) DEFAULT 0,
                total_recharged DECIMAL(10,2) DEFAULT 0,
                total_consumed DECIMAL(10,2) DEFAULT 0,
                free_quota DECIMAL(10,2) DEFAULT 20,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # 2. AI交易记录表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ai_transactions (
                id VARCHAR(36) PRIMARY KEY,
                shop_id VARCHAR(36) NOT NULL,
                type VARCHAR(20) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                balance_after DECIMAL(10,2) NOT NULL,
                description TEXT,
                reference_id VARCHAR(36),
                reference_type VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # 3. AI用量记录表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ai_usage (
                id VARCHAR(36) PRIMARY KEY,
                shop_id VARCHAR(36) NOT NULL,
                provider_id VARCHAR(36),
                model_name VARCHAR(50) NOT NULL,
                model_provider VARCHAR(20) NOT NULL,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                input_cost DECIMAL(10,4) DEFAULT 0,
                output_cost DECIMAL(10,4) DEFAULT 0,
                total_cost DECIMAL(10,4) DEFAULT 0,
                conversation_id VARCHAR(36),
                message_id VARCHAR(36),
                request_data TEXT,
                response_time_ms INTEGER,
                status VARCHAR(20) DEFAULT 'success',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # 4. AI模型价格配置表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ai_model_prices (
                id VARCHAR(36) PRIMARY KEY,
                model_name VARCHAR(50) NOT NULL UNIQUE,
                model_id VARCHAR(50) NOT NULL,
                provider VARCHAR(20) NOT NULL,
                official_input_price DECIMAL(10,4) NOT NULL,
                official_output_price DECIMAL(10,4) NOT NULL,
                discount_normal INTEGER DEFAULT 100,
                discount_bronze INTEGER DEFAULT 85,
                discount_silver INTEGER DEFAULT 75,
                discount_gold INTEGER DEFAULT 60,
                context_length INTEGER,
                max_tokens INTEGER,
                features TEXT,
                icon VARCHAR(10) DEFAULT '🤖',
                is_active BOOLEAN DEFAULT 1,
                is_recommended BOOLEAN DEFAULT 0,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # 5. 充值订单表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS recharge_orders (
                id VARCHAR(36) PRIMARY KEY,
                shop_id VARCHAR(36) NOT NULL,
                order_no VARCHAR(32) NOT NULL UNIQUE,
                amount DECIMAL(10,2) NOT NULL,
                gift_amount DECIMAL(10,2) DEFAULT 0,
                payment_method VARCHAR(20),
                status VARCHAR(20) DEFAULT 'pending',
                paid_at TIMESTAMP,
                transaction_no VARCHAR(64),
                notify_data TEXT,
                notified_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # 6. 服务商结算表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS provider_settlements (
                id VARCHAR(36) PRIMARY KEY,
                provider_id VARCHAR(36) NOT NULL,
                period_start TIMESTAMP NOT NULL,
                period_end TIMESTAMP NOT NULL,
                total_usage DECIMAL(10,4) DEFAULT 0,
                platform_cost DECIMAL(10,4) DEFAULT 0,
                provider_profit DECIMAL(10,4) DEFAULT 0,
                platform_profit DECIMAL(10,4) DEFAULT 0,
                status VARCHAR(20) DEFAULT 'pending',
                settled_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        conn.commit()
        print("[OK] Database tables created")
        
        # 插入默认模型价格数据
        models = [
            ('GPT-4', 'gpt-4', 'openai', 0.215, 0.645, 8192, '["最强推理", "代码生成"]', '🤖', 0, 1),
            ('GPT-4o', 'gpt-4o', 'openai', 0.036, 0.108, 128000, '["速度快", "多模态", "性价比高"]', '⚡', 1, 2),
            ('Claude 3.5', 'claude-3-5-sonnet-20241022', 'anthropic', 0.108, 0.538, 200000, '["长上下文", "安全", "创作"]', '🧠', 0, 3),
            ('Kimi K2.5', 'kimi-k2.5', 'moonshot', 0.012, 0.024, 256000, '["长文本", "中文优化", "高性价比"]', '🌙', 1, 4),
            ('文心一言4.0', 'ernie-bot-4', 'baidu', 0.12, 0.12, 8000, '["中文强", "搜索", "知识"]', '🔴', 0, 5),
            ('通义千问Max', 'qwen-max', 'alibaba', 0.08, 0.08, 8000, '["中文强", "代码", "推理"]', '🟠', 0, 6),
            ('豆包Pro', 'doubao-pro', 'bytedance', 0.016, 0.016, 4000, '["超低价", "中文", "年轻"]', '🟢', 0, 7),
            ('GLM-4', 'glm-4', 'zhipu', 0.10, 0.10, 128000, '["国产", "开源", "多轮"]', '🔵', 0, 8),
        ]
        
        for model in models:
            try:
                conn.execute(text("""
                    INSERT OR IGNORE INTO ai_model_prices 
                    (id, model_name, model_id, provider, official_input_price, official_output_price, 
                     context_length, features, icon, is_recommended, sort_order)
                    VALUES (lower(hex(randomblob(16))), :model_name, :model_id, :provider, 
                            :input_price, :output_price, :context_length, :features, :icon, 
                            :is_recommended, :sort_order)
                """), {
                    'model_name': model[0],
                    'model_id': model[1],
                    'provider': model[2],
                    'input_price': model[3],
                    'output_price': model[4],
                    'context_length': model[5],
                    'features': model[6],
                    'icon': model[7],
                    'is_recommended': model[8],
                    'sort_order': model[9]
                })
            except Exception as e:
                print(f"Insert model {model[0]} failed: {e}")
        
        conn.commit()
        print("[OK] Default model prices inserted")

if __name__ == "__main__":
    create_tables()
    print("\n[OK] Database initialization completed!")
