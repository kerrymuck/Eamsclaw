# EAMS Backend V2 - Docker 配置

## 快速开始

### 1. 构建镜像
```bash
docker build -t eams-backend-v2 .
```

### 2. 运行容器
```bash
docker run -d \
  --name eams-backend \
  -p 8000:8000 \
  -e DATABASE_URL=mysql+aiomysql://root:password@host.docker.internal:3306/eams_v2 \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  eams-backend-v2
```

### 3. 使用 Docker Compose
```bash
docker-compose up -d
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接URL | - |
| REDIS_URL | Redis连接URL | - |
| JWT_SECRET_KEY | JWT密钥 | - |
| DEBUG | 调试模式 | false |
