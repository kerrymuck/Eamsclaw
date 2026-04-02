# EAMS 商户管理端部署教程

> **EAMS (E-commerce AI Merchant Service)** - 电商客服智能体系统商户管理端

## 📋 目录

1. [环境要求](#环境要求)
2. [部署架构](#部署架构)
3. [后端服务部署](#后端服务部署)
4. [商户管理端部署](#商户管理端部署)
5. [Nginx配置](#nginx配置)
6. [Docker部署（推荐）](#docker部署推荐)
7. [常见问题](#常见问题)

---

## 环境要求

### 服务器配置
| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 磁盘 | 20GB | 50GB+ |
| 带宽 | 5Mbps | 10Mbps+ |

### 软件依赖
- **Node.js**: v18.0.0+
- **Python**: v3.9+
- **MySQL**: v8.0+
- **Redis**: v6.0+
- **Nginx**: v1.20+

---

## 部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                         用户浏览器                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      Nginx 反向代理                          │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │ /api/*       │ /merchant/*  │ /admin/*     │             │
│  │ → 后端:8000  │ → 商户端:5175│ → 管理端:5173│             │
│  └──────────────┴──────────────┴──────────────┘             │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐
│ 后端服务      │ │ 商户管理端 │ │ 管理后台  │
│ FastAPI:8000 │ │ Vue3:5175│ │ Vue3:5173│
└──────────────┘ └──────────┘ └──────────┘
        │
        ▼
┌──────────────┬──────────┐
│   MySQL      │  Redis   │
│  (数据存储)   │ (缓存/会话)│
└──────────────┴──────────┘
```

---

## 后端服务部署

### 1. 安装Python依赖

```bash
# 进入后端目录
cd eams-backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=mysql+pymysql://eams_user:your_password@localhost:3306/eams_db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT密钥
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS配置
ALLOWED_HOSTS=["http://localhost:5173", "http://localhost:5175", "https://your-domain.com"]

# 文件上传
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=uploads

# AI配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 3. 初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS eams_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 执行迁移
alembic upgrade head

# 或者使用SQL初始化（首次部署）
mysql -u eams_user -p eams_db < database/init.sql
```

### 4. 启动后端服务

```bash
# 开发模式
python -m app.main

# 生产模式（使用Gunicorn）
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app

# 后台运行（Systemd）
sudo systemctl start eams-backend
```

---

## 商户管理端部署

### 1. 安装Node依赖

```bash
cd eams-merchant

# 使用npm
npm install

# 或使用yarn
yarn install

# 或使用pnpm
pnpm install
```

### 2. 配置API地址

编辑 `vite.config.ts`：

```typescript
export default defineConfig({
  // ...其他配置
  server: {
    port: 5175,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // 后端API地址
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:8000',    // WebSocket地址
        ws: true
      }
    }
  }
})
```

### 3. 配置生产环境

创建 `.env.production`：

```bash
VITE_API_BASE_URL=https://api.your-domain.com
VITE_WS_URL=wss://api.your-domain.com/ws
```

### 4. 构建生产包

```bash
# 开发调试
npm run dev

# 生产构建
npm run build

# 构建输出在 dist/ 目录
```

### 5. 预览生产构建

```bash
npm run preview
```

---

## Nginx配置

### 1. 安装Nginx

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

### 2. 配置Nginx

创建 `/etc/nginx/sites-available/eams`：

```nginx
# 上游服务器
upstream eams_backend {
    server 127.0.0.1:8000;
}

upstream eams_merchant {
    server 127.0.0.1:5175;
}

upstream eams_admin {
    server 127.0.0.1:5173;
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS主配置
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL证书
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 日志
    access_log /var/log/nginx/eams-access.log;
    error_log /var/log/nginx/eams-error.log;

    # 后端API
    location /api/ {
        proxy_pass http://eams_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://eams_backend/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 商户管理端
    location /merchant/ {
        proxy_pass http://eams_merchant/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 管理后台
    location /admin/ {
        proxy_pass http://eams_admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态文件
    location /uploads/ {
        alias /path/to/eams-backend/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 默认入口
    location / {
        root /path/to/eams-merchant/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }
}
```

### 3. 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/eams /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载Nginx
sudo systemctl reload nginx
```

---

## Docker部署（推荐）

### 1. 创建Dockerfile

**后端 Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"]
```

**商户端 Dockerfile:**

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

### 2. Docker Compose配置

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  # MySQL数据库
  mysql:
    image: mysql:8.0
    container_name: eams-mysql
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: eams_db
      MYSQL_USER: eams_user
      MYSQL_PASSWORD: eams_password
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"
    networks:
      - eams-network

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: eams-redis
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - eams-network

  # 后端服务
  backend:
    build:
      context: ./eams-backend
      dockerfile: Dockerfile
    container_name: eams-backend
    environment:
      DATABASE_URL: mysql+pymysql://eams_user:eams_password@mysql:3306/eams_db
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: your-secret-key
    ports:
      - "8000:8000"
    depends_on:
      - mysql
      - redis
    networks:
      - eams-network
    restart: unless-stopped

  # 商户管理端
  merchant:
    build:
      context: ./eams-merchant
      dockerfile: Dockerfile
    container_name: eams-merchant
    ports:
      - "5175:80"
    depends_on:
      - backend
    networks:
      - eams-network
    restart: unless-stopped

  # 管理后台
  admin:
    build:
      context: ./eams-admin
      dockerfile: Dockerfile
    container_name: eams-admin
    ports:
      - "5173:80"
    depends_on:
      - backend
    networks:
      - eams-network
    restart: unless-stopped

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: eams-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./eams-backend/uploads:/var/www/uploads
    depends_on:
      - backend
      - merchant
      - admin
    networks:
      - eams-network
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:

networks:
  eams-network:
    driver: bridge
```

### 3. 一键部署

```bash
# 克隆代码
git clone https://github.com/kerrymuck/Eamsclaw.git
cd Eamsclaw

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

---

## 常见问题

### Q1: 构建失败，提示缺少依赖

```bash
# 清理缓存重新安装
rm -rf node_modules package-lock.json
npm install

# 或者使用--legacy-peer-deps
npm install --legacy-peer-deps
```

### Q2: 后端启动失败，数据库连接错误

```bash
# 检查MySQL服务
sudo systemctl status mysql

# 检查数据库是否存在
mysql -u root -p -e "SHOW DATABASES;"

# 检查用户权限
mysql -u root -p -e "SHOW GRANTS FOR 'eams_user'@'localhost';"
```

### Q3: 前端无法连接后端API

```bash
# 检查后端服务是否运行
curl http://localhost:8000/health

# 检查CORS配置
# 确保ALLOWED_HOSTS包含前端域名

# 检查防火墙
sudo ufw status
sudo ufw allow 8000
```

### Q4: WebSocket连接失败

```bash
# 检查Nginx WebSocket配置
# 确保包含以下配置：
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### Q5: 文件上传失败

```bash
# 检查上传目录权限
chmod -R 755 /path/to/eams-backend/uploads
chown -R www-data:www-data /path/to/eams-backend/uploads

# 检查Nginx上传限制
client_max_body_size 50M;
```

---

## 系统服务配置

### Systemd服务文件

**后端服务:** `/etc/systemd/system/eams-backend.service`

```ini
[Unit]
Description=EAMS Backend Service
After=network.target mysql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/eams-backend
Environment=PATH=/path/to/eams-backend/venv/bin
ExecStart=/path/to/eams-backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable eams-backend
sudo systemctl start eams-backend
sudo systemctl status eams-backend
```

---

## 访问地址

部署完成后，可通过以下地址访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| 商户管理端 | http://your-domain.com/merchant | 商家登录入口 |
| 管理后台 | http://your-domain.com/admin | 平台管理员入口 |
| API文档 | http://your-domain.com/api/docs | Swagger文档 |
| 健康检查 | http://your-domain.com/api/health | 服务状态 |

---

## 维护命令

```bash
# 查看服务状态
sudo systemctl status eams-backend
sudo docker-compose ps

# 查看日志
tail -f /var/log/nginx/eams-error.log
docker-compose logs -f backend

# 备份数据库
mysqldump -u eams_user -p eams_db > backup_$(date +%Y%m%d).sql

# 更新部署
git pull
docker-compose up -d --build
```

---

*文档版本: v1.0*  
*更新日期: 2026-04-02*  
*作者: 龙猫技术团队*
