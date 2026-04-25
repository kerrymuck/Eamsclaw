# EAMS V2 数据库初始化脚本

## 创建数据库

```sql
CREATE DATABASE IF NOT EXISTS eams_v2 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE eams_v2;
```

## 数据表说明

### 用户相关
- `users` - 用户表
- `merchants` - 商户表
- `providers` - 服务商表

### 套餐相关
- `packages` - 套餐表
- `merchant_packages` - 商户套餐订阅记录

### AI相关
- `ai_accounts` - AI账户表
- `ai_models` - AI模型配置表
- `ai_usage_records` - AI使用记录

### 支付相关
- `recharge_records` - 充值记录
- `financial_records` - 财务流水

### 系统相关
- `system_settings` - 系统设置

## 初始化命令

```bash
# 使用 SQLAlchemy 自动创建表
python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"

# 或使用 Alembic 迁移
alembic init alembic
alembic revision --autogenerate -m "init"
alembic upgrade head
```
