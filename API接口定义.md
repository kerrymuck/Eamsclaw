# EAMS API接口定义文档

**文档版本**：v1.0
**设计人**：青龙
**日期**：2026-03-16
**项目**：电商客服智能体（EAMS）
**Base URL**：`https://api.eams.example.com/v1`

---

## 目录

1. [通用规范](#1-通用规范)
2. [认证相关](#2-认证相关)
3. [对话服务API](#3-对话服务api)
4. [知识库API](#4-知识库api)
5. [平台对接API](#5-平台对接api)
6. [数据统计API](#6-数据统计api)
7. [WebSocket实时通信](#7-websocket实时通信)
8. [数据模型定义](#8-数据模型定义)

---

## 1. 通用规范

### 1.1 请求规范
- 所有请求使用 JSON 格式
- Content-Type: `application/json`
- 时间格式：ISO 8601 (`2026-03-16T12:00:00Z`)

### 1.2 响应格式
```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

### 1.3 错误码规范

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 40001 | 参数错误 |
| 40002 | 缺少必填参数 |
| 40100 | 未认证 |
| 40101 | Token过期 |
| 40300 | 无权限 |
| 40400 | 资源不存在 |
| 42900 | 请求过于频繁 |
| 50000 | 服务器内部错误 |
| 50001 | AI服务异常 |
| 50002 | 平台API异常 |

---

## 2. 认证相关

### 2.1 登录
```
POST /auth/login
```

**请求参数**：
```json
{
  "username": "admin",
  "password": "hashed_password"
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600,
    "token_type": "Bearer"
  }
}
```

### 2.2 刷新Token
```
POST /auth/refresh
```

---

## 3. 对话服务API

### 3.1 发送消息（用户→系统）
```
POST /dialog/message
```

**请求参数**：
```json
{
  "platform": "taobao",
  "shop_id": "shop_12345",
  "user_id": "user_67890",
  "content": "这个商品什么时候发货？",
  "msg_type": "text"
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "message_id": "msg_uuid",
    "conversation_id": "conv_uuid",
    "reply": {
      "content": "亲，一般24小时内发货哦~",
      "type": "text",
      "intent": "shipping_inquiry",
      "confidence": 0.95
    },
    "created_at": "2026-03-16T12:00:00Z"
  }
}
```

### 3.2 获取对话列表
```
GET /dialog/conversations?shop_id={shop_id}&status={status}&page={page}&size={size}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "total": 100,
    "items": [
      {
        "id": "conv_uuid",
        "platform": "taobao",
        "platform_user_id": "user_67890",
        "user_name": "买家昵称",
        "status": "active",
        "unread_count": 3,
        "last_message": {
          "content": "好的谢谢",
          "direction": "in",
          "created_at": "2026-03-16T11:58:00Z"
        },
        "created_at": "2026-03-16T10:00:00Z"
      }
    ]
  }
}
```

### 3.3 获取对话详情
```
GET /dialog/conversations/{conversation_id}/messages
```

### 3.4 转人工
```
POST /dialog/handoff
```

**请求参数**：
```json
{
  "conversation_id": "conv_uuid",
  "reason": "complex_issue",
  "note": "用户要求退货退款，需要人工处理"
}
```

### 3.5 关闭对话
```
PUT /dialog/conversations/{conversation_id}/close
```

---

## 4. 知识库API

### 4.1 查询知识库
```
GET /knowledge/search?q={query}&shop_id={shop_id}&limit={limit}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "query": "发货时间",
    "results": [
      {
        "id": "kb_uuid",
        "question": "什么时候发货？",
        "answer": "亲，我们一般24小时内发货，特殊情况会提前告知~",
        "category": "物流",
        "score": 0.92
      }
    ]
  }
}
```

### 4.2 添加知识
```
POST /knowledge
```

**请求参数**：
```json
{
  "shop_id": "shop_12345",
  "category": "物流",
  "question": "什么时候发货？",
  "answer": "亲，我们一般24小时内发货~",
  "keywords": ["发货", "快递", "物流"]
}
```

### 4.3 更新知识
```
PUT /knowledge/{knowledge_id}
```

### 4.4 删除知识
```
DELETE /knowledge/{knowledge_id}
```

### 4.5 批量导入
```
POST /knowledge/batch-import
```

**请求**：multipart/form-data (Excel/CSV文件)

---

## 5. 平台对接API

### 5.1 获取店铺列表
```
GET /platform/shops
```

### 5.2 绑定店铺
```
POST /platform/shops/bind
```

**请求参数**：
```json
{
  "platform": "taobao",
  "auth_code": "auth_code_from_platform",
  "shop_name": "店铺名称"
}
```

### 5.3 获取订单信息
```
GET /platform/orders/{order_id}?shop_id={shop_id}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "order_id": "order_uuid",
    "platform": "taobao",
    "platform_order_id": "123456789",
    "status": "shipped",
    "total_amount": 199.00,
    "items": [
      {
        "sku_id": "sku_001",
        "name": "商品名称",
        "quantity": 2,
        "price": 99.50
      }
    ],
    "logistics": {
      "company": "顺丰",
      "tracking_no": "SF123456789"
    },
    "created_at": "2026-03-15T10:00:00Z"
  }
}
```

### 5.4 发送平台消息
```
POST /platform/message/send
```

### 5.5 平台授权状态
```
GET /platform/auth-status?shop_id={shop_id}
```

---

## 6. 数据统计API

### 6.1 实时概览
```
GET /analytics/dashboard?shop_id={shop_id}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "today": {
      "total_conversations": 156,
      "total_messages": 892,
      "active_conversations": 23,
      "avg_response_time": 3.5,
      "handoff_rate": 0.08
    },
    "comparison": {
      "conversation_change": 0.15,
      "response_time_change": -0.10
    }
  }
}
```

### 6.2 对话统计
```
GET /analytics/conversations?shop_id={shop_id}&start_date={start}&end_date={end}
```

### 6.3 响应时间分析
```
GET /analytics/response-time?shop_id={shop_id}&period={period}
```

### 6.4 意图分布
```
GET /analytics/intents?shop_id={shop_id}&start_date={start}&end_date={end}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "distribution": [
      {"intent": "shipping_inquiry", "count": 450, "percentage": 0.35},
      {"intent": "return_request", "count": 200, "percentage": 0.15},
      {"intent": "product_inquiry", "count": 350, "percentage": 0.27}
    ]
  }
}
```

### 6.5 导出报表
```
POST /analytics/export
```

---

## 7. WebSocket实时通信

### 7.1 连接地址
```
wss://api.eams.example.com/v1/ws
```

### 7.2 认证
连接时在 query 中携带 token：
```
wss://api.eams.example.com/v1/ws?token={access_token}
```

### 7.3 消息格式

**客户端 → 服务端**：
```json
{
  "type": "subscribe",
  "channel": "shop_12345",
  "action": "conversations"
}
```

**服务端 → 客户端**：
```json
{
  "type": "message",
  "channel": "shop_12345",
  "data": {
    "event": "new_message",
    "conversation_id": "conv_uuid",
    "message": {
      "id": "msg_uuid",
      "content": "用户新消息",
      "direction": "in",
      "created_at": "2026-03-16T12:00:00Z"
    }
  }
}
```

### 7.4 事件类型

| 事件 | 说明 |
|------|------|
| `new_message` | 新消息 |
| `conversation_created` | 新对话创建 |
| `conversation_closed` | 对话关闭 |
| `handoff_requested` | 转人工请求 |
| `typing` | 对方正在输入 |

---

## 8. 数据模型定义

### 8.1 Pydantic Schema

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PlatformType(str, Enum):
    TAOBAO = "taobao"
    JD = "jd"
    PDD = "pdd"

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    ORDER = "order"
    PRODUCT = "product"

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    PENDING = "pending"

# 消息模型
class Message(BaseModel):
    id: str = Field(..., description="消息ID")
    conversation_id: str
    direction: str = Field(..., regex="^(in|out)$")
    content: str
    msg_type: MessageType = MessageType.TEXT
    intent: Optional[str] = None
    intent_confidence: Optional[float] = Field(None, ge=0, le=1)
    created_at: datetime
    
    class Config:
        orm_mode = True

# 对话模型
class Conversation(BaseModel):
    id: str
    platform: PlatformType
    platform_user_id: str
    user_name: Optional[str] = None
    shop_id: str
    status: ConversationStatus
    unread_count: int = 0
    last_message: Optional[Message] = None
    created_at: datetime
    updated_at: datetime

# 知识库模型
class KnowledgeItem(BaseModel):
    id: str
    shop_id: str
    category: str
    question: str
    answer: str
    keywords: List[str] = []
    hit_count: int = 0
    created_at: datetime
    updated_at: datetime

# 对话请求
class DialogRequest(BaseModel):
    platform: PlatformType
    shop_id: str
    user_id: str
    content: str = Field(..., min_length=1, max_length=2000)
    msg_type: MessageType = MessageType.TEXT
    conversation_id: Optional[str] = None

# 对话响应
class DialogResponse(BaseModel):
    message_id: str
    conversation_id: str
    reply: Message
    suggested_actions: List[str] = []

# 统计概览
class DashboardStats(BaseModel):
    total_conversations: int
    total_messages: int
    active_conversations: int
    avg_response_time: float  # 秒
    handoff_count: int
    handoff_rate: float
```

---

## 9. 平台回调接口

各平台消息推送回调：

### 9.1 淘宝回调
```
POST /webhook/taobao
```

### 9.2 京东回调
```
POST /webhook/jd
```

### 9.3 拼多多回调
```
POST /webhook/pdd
```

**统一处理流程**：
1. 验证签名
2. 解析消息
3. 存入消息队列
4. 返回成功响应

---

**文档完成时间**：2026-03-16 12:15
**状态**：待评审
