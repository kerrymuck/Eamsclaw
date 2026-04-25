# EAMS Backend Admin

EAMS超级管理员后台API服务

## 技术栈

- NestJS
- TypeORM
- PostgreSQL
- Redis
- JWT

## 安装

```bash
npm install
```

## 环境变量

创建 `.env` 文件:

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_DATABASE=eams_admin

# JWT配置
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=7d

# 服务器端口
PORT=8001
```

## 运行

```bash
# 开发模式
npm run start:dev

# 生产模式
npm run build
npm run start:prod
```

## API文档

启动后访问: http://localhost:8001/api/docs

## 默认账号

- 用户名: admin
- 密码: admin123
