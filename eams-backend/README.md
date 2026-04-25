# EAMS 后端服务

电商客服智能体系统 (E-commerce Agent Management System) 后端API服务。

## 技术栈

- **框架**: FastAPI
- **数据库**: PostgreSQL + SQLAlchemy (异步)
- **缓存**: Redis
- **消息队列**: RabbitMQ (可选)
- **定时任务**: APScheduler
- **AI服务**: OpenAI API

## 项目结构

```
eams-backend/
├── alembic/                # 数据库迁移
│   ├── versions/          # 迁移脚本
│   ├── env.py             # 迁移环境配置
│   └── script.py.mako     # 迁移模板
├── app/
│   ├── api/               # API路由
│   │   └── v1/            # API版本1
│   │       ├── auth.py    # 认证相关
│   │       ├── dialog.py  # 对话管理
│   │       ├── knowledge.py  # 知识库
│   │       ├── platform.py   # 平台对接
│   │       ├── analytics.py  # 数据统计
│   │       ├── upload.py     # 文件上传
│   │       └── settings.py   # 系统设置
│   ├── core/              # 核心配置
│   │   ├── config.py      # 应用配置
│   │   └── database.py    # 数据库连接
│   ├── models/            # 数据模型
│   │   ├── user.py        # 用户/店铺
│   │   ├── conversation.py   # 对话/消息
│   │   ├── knowledge.py   # 知识库
│   │   ├── stats.py       # 统计数据
│   │   ├── ai.py          # AI相关
│   │   ├── system.py      # 系统设置
│   │   └── platform_config.py  # 平台配置
│   ├── services/          # 业务逻辑
│   │   ├── ai_service.py  # AI服务
│   │   ├── message_processor.py  # 消息处理
│   │   └── platform/      # 平台适配器
│   ├── tasks/             # 定时任务
│   │   └── scheduler.py   # 任务调度器
│   ├── websocket/         # WebSocket
│   │   └── chat.py        # 实时通信
│   └── main.py            # 应用入口
├── uploads/               # 上传文件目录
├── alembic.ini            # Alembic配置
├── requirements.txt       # 依赖列表
├── .env.example           # 环境变量示例
├── start.bat              # Windows启动脚本
├── start.sh               # Linux/Mac启动脚本
└── README.md              # 项目说明
```

## 快速开始

### 1. 环境要求

- Python 3.10+
- PostgreSQL 14+
- Redis 6+ (可选)

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，修改数据库连接等配置
```

### 4. 初始化数据库

```bash
# 创建数据库
createdb eams

# 执行迁移
alembic upgrade head
```

### 5. 启动服务

```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# 或直接使用 uvicorn
uvicorn app.main:app --reload
```

服务启动后访问:
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## API 模块

### 认证模块 (`/api/v1/auth`)
- POST `/login` - 用户登录
- POST `/register` - 用户注册
- POST `/refresh` - 刷新Token
- GET `/me` - 获取当前用户信息
- PUT `/me` - 更新用户信息
- POST `/change-password` - 修改密码
- GET `/shops` - 获取店铺列表
- POST `/shops` - 创建店铺
- GET `/shops/{shop_id}` - 获取店铺详情
- PUT `/shops/{shop_id}` - 更新店铺
- GET `/shops/{shop_id}/members` - 获取成员列表
- POST `/shops/{shop_id}/members` - 添加成员
- DELETE `/shops/{shop_id}/members/{user_id}` - 移除成员

### 对话模块 (`/api/v1/dialog`)
- GET `/conversations` - 获取对话列表
- GET `/conversations/{conversation_id}` - 获取对话详情
- GET `/conversations/{conversation_id}/messages` - 获取消息列表
- POST `/conversations/{conversation_id}/messages` - 发送消息
- POST `/conversations/{conversation_id}/assign` - 分配对话
- POST `/conversations/{conversation_id}/close` - 关闭对话
- POST `/conversations/{conversation_id}/tags` - 更新标签
- GET `/handoffs` - 获取转人工列表
- POST `/handoffs/{handoff_id}/accept` - 接受转人工
- POST `/handoffs/{handoff_id}/resolve` - 解决转人工

### 知识库模块 (`/api/v1/knowledge`)
- GET `/categories` - 获取分类列表
- POST `/categories` - 创建分类
- PUT `/categories/{category_id}` - 更新分类
- DELETE `/categories/{category_id}` - 删除分类
- GET `/knowledges` - 获取知识库列表
- GET `/knowledges/{knowledge_id}` - 获取知识库详情
- POST `/knowledges` - 创建知识库条目
- PUT `/knowledges/{knowledge_id}` - 更新知识库条目
- DELETE `/knowledges/{knowledge_id}` - 删除知识库条目
- GET `/search` - 智能搜索

### 平台对接模块 (`/api/v1/platform`)
- GET `/platforms` - 获取平台列表
- POST `/platforms/bind` - 绑定平台
- POST `/platforms/{platform_id}/auth` - 平台授权
- DELETE `/platforms/{platform_id}` - 解绑平台
- POST `/webhook/{platform_type}` - 接收平台消息
- GET `/orders/{platform_type}/{order_id}` - 查询订单

### 数据统计模块 (`/api/v1/analytics`)
- GET `/dashboard` - 仪表盘数据
- GET `/daily` - 每日统计
- GET `/hourly` - 小时统计
- GET `/intents` - 意图统计
- GET `/agents` - 客服统计
- GET `/realtime` - 实时统计

### 文件上传模块 (`/api/v1/upload`)
- POST `/image` - 上传图片
- POST `/file` - 上传文件
- GET `/images/{user_id}/{date}/{filename}` - 获取图片
- GET `/files/{user_id}/{date}/{filename}` - 获取文件
- DELETE `/delete` - 删除文件

### 系统设置模块 (`/api/v1/settings`)
- GET `/shop` - 获取店铺设置
- PUT `/shop` - 更新店铺信息
- GET `/ai` - 获取AI设置
- PUT `/ai` - 更新AI设置
- GET `/conversation` - 获取对话设置
- PUT `/conversation` - 更新对话设置
- GET `/system` - 获取系统设置(管理员)
- PUT `/system` - 更新系统设置(管理员)

### WebSocket (`/ws/chat`)
连接URL: `ws://localhost:8000/ws/chat?token={jwt_token}`

消息类型:
- `ping/pong` - 心跳检测
- `send_message` - 发送消息
- `typing` - 正在输入
- `mark_read` - 标记已读

推送类型:
- `new_message` - 新消息通知
- `conversation_update` - 会话更新
- `handoff_request` - 转人工请求

## 数据库模型

### 核心表
- `users` - 用户表
- `shops` - 店铺表
- `shop_members` - 店铺成员表
- `platform_configs` - 平台配置表
- `shop_platform_auths` - 店铺平台授权表

### 业务表
- `conversations` - 对话表
- `messages` - 消息表
- `handoffs` - 转人工表
- `knowledge_categories` - 知识库分类表
- `knowledge` - 知识库条目表

### 统计表
- `daily_stats` - 日统计表
- `hourly_stats` - 小时统计表
- `intent_stats` - 意图统计表

### 其他表
- `intent_logs` - 意图日志表
- `model_configs` - 模型配置表
- `settings` - 系统设置表
- `audit_logs` - 审计日志表
- `platform_webhook_logs` - Webhook日志表

## 定时任务

- **每小时统计** - 计算小时统计数据
- **每日统计** - 每天凌晨1点计算日统计数据
- **意图统计** - 每天凌晨2点计算意图统计数据
- **自动关闭会话** - 每小时检查并关闭超时会话

## 开发指南

### 添加新的API

1. 在 `app/api/v1/` 下创建新的路由文件
2. 在 `app/main.py` 中注册路由
3. 添加对应的模型（如需要）
4. 创建数据库迁移: `alembic revision --autogenerate -m "描述"`

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "add new table"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 部署

### Docker部署 (待补充)

### 生产环境注意事项

1. 修改 `.env` 中的 `SECRET_KEY`
2. 配置正确的数据库连接
3. 配置Redis和RabbitMQ
4. 设置 `DEBUG=false`
5. 配置正确的 `ALLOWED_HOSTS`
6. 使用HTTPS
7. 配置日志收集

## 许可证

MIT License
