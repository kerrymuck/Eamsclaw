# EAMS Backend V2

FastAPI + SQLAlchemy 后端项目

## 项目结构

```
eams-backend-v2/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── cache.py             # Redis缓存
│   ├── exceptions.py        # 异常处理
│   ├── dependencies.py      # 依赖注入
│   ├── middlewares/         # 中间件
│   │   ├── __init__.py
│   │   ├── auth.py          # JWT认证中间件
│   │   └── cors.py          # CORS中间件
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py      # 认证相关
│   │       ├── merchants.py # 商户管理
│   │       ├── packages.py  # 套餐管理
│   │       ├── providers.py # 服务商管理
│   │       ├── ai_power.py  # AI算力中心
│   │       ├── payment.py   # 支付系统
│   │       └── settings.py  # 系统设置
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py          # 基础模型
│   │   ├── user.py          # 用户模型
│   │   ├── merchant.py      # 商户模型
│   │   ├── package.py       # 套餐模型
│   │   ├── provider.py      # 服务商模型
│   │   ├── ai_account.py    # AI账户模型
│   │   ├── recharge.py      # 充值记录
│   │   └── setting.py       # 系统设置
│   ├── schemas/             # Pydantic模型
│   │   ├── __init__.py
│   │   ├── base.py          # 基础响应
│   │   ├── auth.py          # 认证相关
│   │   ├── merchant.py      # 商户相关
│   │   ├── package.py       # 套餐相关
│   │   ├── ai.py            # AI相关
│   │   └── payment.py       # 支付相关
│   ├── services/            # 业务逻辑
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证服务
│   │   ├── merchant.py      # 商户服务
│   │   ├── ai_power.py      # AI算力服务
│   │   └── payment.py       # 支付服务
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── security.py      # 安全工具
│       └── helpers.py       # 辅助函数
├── alembic/                 # 数据库迁移
├── tests/                   # 测试
├── requirements.txt         # 依赖
├── .env.example            # 环境变量示例
└── README.md               # 项目说明
```

## 快速开始

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件
```

3. 运行迁移
```bash
alembic upgrade head
```

4. 启动服务
```bash
uvicorn app.main:app --reload
```

## API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
