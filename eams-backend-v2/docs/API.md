# EAMS Backend V2 API 接口文档

**基础URL**: `http://localhost:8000/api/v1`

---

## 认证模块

### 登录
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": 1,
      "username": "admin",
      "role": "super_admin"
    }
  }
}
```

### 刷新Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 商户管理

### 获取商户列表
```http
GET /merchants?page=1&page_size=10
Authorization: Bearer {token}
```

### 创建商户
```http
POST /merchants
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "测试商户",
  "company_name": "测试公司",
  "contact_name": "张三",
  "contact_phone": "13800138000"
}
```

### 获取商户详情
```http
GET /merchants/{merchant_id}
Authorization: Bearer {token}
```

### 更新商户
```http
PUT /merchants/{merchant_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "新名称",
  "contact_phone": "13900139000"
}
```

### 删除商户
```http
DELETE /merchants/{merchant_id}
Authorization: Bearer {token}
```

---

## 套餐管理

### 获取套餐列表
```http
GET /packages?page=1&page_size=10
Authorization: Bearer {token}
```

### 创建套餐
```http
POST /packages
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "基础版",
  "type": "basic",
  "price": 99.00,
  "ai_tokens": 100000,
  "validity_days": 30
}
```

---

## AI算力中心

### 获取模型列表
```http
GET /ai/models
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 200,
  "data": [
    {
      "id": "moonshot/kimi-k2.5",
      "name": "Kimi K2.5",
      "provider": "moonshot",
      "input_price": 0.001,
      "output_price": 0.002,
      "max_tokens": 8192,
      "response_time": 800,
      "accuracy": 95,
      "star_rating": 5
    }
  ]
}
```

### 获取账户信息
```http
GET /ai/account
Authorization: Bearer {token}
```

### AI对话
```http
POST /ai/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "model": "moonshot/kimi-k2.5",
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

### 获取使用统计
```http
GET /ai/usage?days=7
Authorization: Bearer {token}
```

---

## 支付系统

### 创建充值订单
```http
POST /payment/recharge
Authorization: Bearer {token}
Content-Type: application/json

{
  "amount": 100.00,
  "payment_method": "wechat"
}
```

### 获取充值记录
```http
GET /payment/orders?page=1&page_size=10
Authorization: Bearer {token}
```

---

## 财务管理

### 获取财务流水
```http
GET /financial?page=1&page_size=10
Authorization: Bearer {token}
```

### 获取财务统计
```http
GET /financial/statistics?days=30
Authorization: Bearer {token}
```

---

## 系统设置

### 获取设置列表
```http
GET /settings?group=payment
Authorization: Bearer {token}
```

### 更新设置
```http
PUT /settings/{key}
Authorization: Bearer {token}
Content-Type: application/json

{
  "value": "new_value"
}
```

### 批量更新设置
```http
POST /settings/batch
Authorization: Bearer {token}
Content-Type: application/json

{
  "settings": [
    {"key": "wechat_app_id", "value": "wx123456"},
    {"key": "wechat_mch_id", "value": "1234567890"}
  ]
}
```

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 参数验证失败 |
| 500 | 服务器内部错误 |

---

## 支持的AI模型

| 提供商 | 模型 | 输入价格 | 输出价格 |
|--------|------|----------|----------|
| Moonshot | kimi-k2.5 | 0.001/1K | 0.002/1K |
| OpenAI | gpt-4 | 0.03/1K | 0.06/1K |
| OpenAI | gpt-3.5-turbo | 0.0015/1K | 0.002/1K |
| Anthropic | claude-3-opus | 0.015/1K | 0.075/1K |
| Anthropic | claude-3-sonnet | 0.003/1K | 0.015/1K |
| DeepSeek | deepseek-chat | 0.001/1K | 0.002/1K |
| Google | gemini-pro | 0.0005/1K | 0.0015/1K |
| 阿里云 | 通义千问 | 0.002/1K | 0.006/1K |
| 字节 | 豆包 | 0.0008/1K | 0.002/1K |
| 零一万物 | Yi | 0.002/1K | 0.002/1K |
