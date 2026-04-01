# EAMS 项目云端部署指南

**项目位置**: `E:\EAMS-Project`  
**创建时间**: 2026-03-25  
**版本**: v1.0.0

---

## 📁 项目结构

```
EAMS-Project/
├── eams-backend/              # FastAPI后端服务
│   ├── app/
│   │   ├── api/v1/           # API接口
│   │   ├── models/           # 数据模型
│   │   ├── services/         # 业务逻辑
│   │   │   └── platform/     # 平台适配器(32平台)
│   │   ├── websocket/        # WebSocket通信
│   │   └── main.py           # 应用入口
│   ├── alembic/              # 数据库迁移
│   └── requirements.txt      # Python依赖
│
├── eams-frontend/             # Vue3管理面板
│   ├── src/
│   │   ├── views/            # 11个页面
│   │   ├── components/       # 公共组件
│   │   ├── router/           # 路由
│   │   ├── stores/           # Pinia状态
│   │   └── config/platforms.ts # 32平台配置
│   └── package.json
│
├── eams-client/               # 用户端聊天组件
│   └── src/components/ChatWidget/
│
├── eams-merchant/             # 商家端
│   └── src/views/             # 5个页面
│
├── daily_logs/                # 开发日志
├── daily_reports/             # 日报
└── docs/                      # 项目文档
    ├── CORE_ARCHITECTURE.md
    ├── DATABASE_SCHEMA.md
    ├── MULTI_SHOP_DESIGN.md
    ├── PLATFORM_CONFIG.md
    └── PLATFORM_EXTENSION_DESIGN.md
```

---

## 🚀 部署步骤

### 1. 后端部署 (eams-backend)

```bash
cd eams-backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库、Redis等

# 数据库迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. 前端部署 (eams-frontend)

```bash
cd eams-frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 部署dist目录到Nginx/Apache
```

Nginx配置示例:
```nginx
server {
    listen 80;
    server_name eams-admin.yourdomain.com;
    
    location / {
        root /var/www/eams-frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 用户端部署 (eams-client)

```bash
cd eams-client
npm install
npm run build
# 部署dist目录到CDN或静态服务器
```

### 4. 商家端部署 (eams-merchant)

```bash
cd eams-merchant
npm install
npm run build
# 部署dist目录到静态服务器
```

---

## ☁️ 云端服务器推荐配置

### 方案一：阿里云 ECS

```
配置: 2核4G
系统: CentOS 7.9 / Ubuntu 20.04
带宽: 5Mbps
存储: 100GB SSD
数据库: RDS MySQL 5.7
缓存: Redis 6.0
```

### 方案二：腾讯云 CVM

```
配置: 2核4G
系统: CentOS 7.9
带宽: 5Mbps
存储: 100GB SSD
数据库: TencentDB for MySQL
缓存: Tencent Redis
```

### 方案三：Docker Compose 部署

```yaml
version: '3.8'

services:
  backend:
    build: ./eams-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/eams
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build: ./eams-frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=eams
      - POSTGRES_PASSWORD=yourpassword
      - POSTGRES_DB=eams
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## 📋 环境变量配置

### 后端 (.env)

```env
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/eams

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT密钥
SECRET_KEY=your-secret-key-here

# AI模型API密钥
OPENAI_API_KEY=sk-...
KIMI_API_KEY=...

# 平台API密钥
TAOBAO_APP_KEY=...
TAOBAO_APP_SECRET=...
JD_APP_KEY=...
...
```

### 前端 (.env.production)

```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com/ws
```

---

## 🔒 安全配置

1. **HTTPS**: 使用SSL证书启用HTTPS
2. **防火墙**: 仅开放80/443/8000端口
3. **数据库**: 禁用root远程登录，创建专用账号
4. **备份**: 每日自动备份数据库
5. **监控**: 配置日志监控和告警

---

## 📊 性能优化

1. **CDN**: 静态资源使用CDN加速
2. **缓存**: Redis缓存热点数据
3. **数据库**: 添加索引优化查询
4. **前端**: 启用Gzip压缩、懒加载
5. **后端**: 使用异步处理、连接池

---

## 🔄 CI/CD 流程

```yaml
# .github/workflows/deploy.yml
name: Deploy EAMS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /var/www/EAMS-Project
            git pull
            docker-compose down
            docker-compose up -d --build
```

---

## 📞 联系方式

- **项目负责人**: Boss
- **技术负责人**: 龙猫 (Totoro)
- **创建时间**: 2026-03-25

---

*忠于祖国，忠于人民，忠于Boss*
