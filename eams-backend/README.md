# EAMS Backend

电商客服智能体后端服务

## 技术栈

- Python 3.11+
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL 14+
- Redis
- RabbitMQ
- Celery

## 项目结构

```
eams-backend/
├── app/
│   ├── api/              # API路由
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── dialog.py
│   │   │   ├── knowledge.py
│   │   │   ├── platform.py
│   │   │   └── analytics.py
│   │   └── deps.py
│   ├── core/             # 核心配置
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── models/           # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── shop.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   └── knowledge.py
│   ├── services/         # 业务逻辑
│   │   ├── dialog_service.py
│   │   ├── ai_service.py
│   │   ├── platform_service.py
│   │   └── analytics_service.py
│   ├── utils/            # 工具函数
│   │   ├── datetime.py
│   │   ├── validators.py
│   │   └── helpers.py
│   └── main.py           # 应用入口
├── alembic/              # 数据库迁移
├── tests/                # 测试
├── requirements.txt
└── Dockerfile
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 运行迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload
```

## API文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发团队

- 架构：玄武
- 后端：青龙
- AI：朱雀
