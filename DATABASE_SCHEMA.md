# EAMS 数据库模型设计

## 核心实体关系

```
Merchant (商家)
  └── Shop (店铺) [1:N]
       ├── Conversation (会话) [1:N]
       │    └── Message (消息) [1:N]
       ├── Order (订单) [1:N]
       └── KnowledgeEntry (知识库条目) [1:N]
  
User (用户)
  ├── ShopMember (店铺成员) [1:N]
  └── Conversation (会话) [1:N]

Customer (客户)
  ├── Conversation (会话) [1:N]
  └── Order (订单) [1:N]
```

---

## 商家/店铺模块

### Merchant (商家)
```sql
CREATE TABLE merchants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL COMMENT '商家名称',
    owner_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/inactive',
    settings JSONB DEFAULT '{}' COMMENT '全局配置',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Shop (店铺)
```sql
CREATE TABLE shops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchants(id),
    name VARCHAR(100) NOT NULL COMMENT '店铺名称',
    platform VARCHAR(20) NOT NULL COMMENT '平台: taobao/jd/pdd',
    platform_shop_id VARCHAR(100) NOT NULL COMMENT '平台店铺ID',
    platform_auth JSONB COMMENT '平台授权信息',
    auth_status VARCHAR(20) DEFAULT 'pending' COMMENT '授权状态: active/expired/pending',
    auth_expire_time TIMESTAMP COMMENT '授权过期时间',
    logo VARCHAR(500) COMMENT '店铺Logo',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/inactive',
    settings JSONB DEFAULT '{}' COMMENT '店铺配置',
    today_orders INTEGER DEFAULT 0 COMMENT '今日订单数',
    today_sales DECIMAL(12,2) DEFAULT 0 COMMENT '今日销售额',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_shops_merchant ON shops(merchant_id);
CREATE INDEX idx_shops_platform ON shops(platform);
```

### ShopMember (店铺成员)
```sql
CREATE TABLE shop_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shops(id),
    user_id UUID NOT NULL REFERENCES users(id),
    role VARCHAR(20) DEFAULT 'agent' COMMENT '角色: owner/admin/agent',
    permissions JSONB DEFAULT '[]' COMMENT '权限列表',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(shop_id, user_id)
);
```

---

## 用户/客户模块

### User (系统用户)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100),
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    avatar VARCHAR(500),
    status VARCHAR(20) DEFAULT 'active',
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Customer (客户)
```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchants(id),
    -- 跨平台身份识别
    phone VARCHAR(20) COMMENT '手机号(脱敏)',
    phone_hash VARCHAR(64) COMMENT '手机号哈希(用于匹配)',
    -- 各平台ID
    taobao_user_id VARCHAR(100),
    jd_user_id VARCHAR(100),
    pdd_user_id VARCHAR(100),
    -- 用户画像
    name VARCHAR(50) COMMENT '客户昵称',
    avatar VARCHAR(500),
    total_spent DECIMAL(12,2) DEFAULT 0 COMMENT '累计消费',
    order_count INTEGER DEFAULT 0 COMMENT '订单数量',
    tags JSONB DEFAULT '[]' COMMENT '客户标签',
    notes TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_merchant ON customers(merchant_id);
CREATE INDEX idx_customers_phone_hash ON customers(phone_hash);
```

---

## 对话模块

### Conversation (会话)
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shops(id),
    customer_id UUID NOT NULL REFERENCES customers(id),
    agent_id UUID REFERENCES users(id) COMMENT '当前客服ID',
    
    -- 会话状态
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/pending_handoff/closed',
    ai_status VARCHAR(20) DEFAULT 'handling' COMMENT 'AI状态: handling/need_human/human_closed',
    
    -- 平台信息
    platform VARCHAR(20) NOT NULL,
    platform_conversation_id VARCHAR(100) COMMENT '平台会话ID',
    
    -- 统计
    message_count INTEGER DEFAULT 0,
    unread_count INTEGER DEFAULT 0,
    ai_message_count INTEGER DEFAULT 0,
    
    -- 时间
    last_message_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    
    -- 标签
    tags JSONB DEFAULT '[]',
    priority INTEGER DEFAULT 0 COMMENT '优先级'
);

CREATE INDEX idx_conversations_shop ON conversations(shop_id);
CREATE INDEX idx_conversations_customer ON conversations(customer_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_last_message ON conversations(last_message_at DESC);
```

### Message (消息)
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    
    -- 发送者
    sender_type VARCHAR(20) NOT NULL COMMENT '类型: customer/agent/ai/system',
    sender_id UUID COMMENT '发送者ID',
    sender_name VARCHAR(50) COMMENT '发送者名称',
    
    -- 消息内容
    content_type VARCHAR(20) DEFAULT 'text' COMMENT '类型: text/image/product/order',
    content TEXT NOT NULL,
    
    -- 平台信息
    platform VARCHAR(20),
    platform_message_id VARCHAR(100),
    
    -- AI相关
    ai_confidence DECIMAL(3,2) COMMENT 'AI置信度',
    ai_intent VARCHAR(50) COMMENT 'AI识别的意图',
    
    -- 状态
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created ON messages(created_at DESC);
```

---

## 订单模块

### Order (订单)
```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shops(id),
    customer_id UUID NOT NULL REFERENCES customers(id),
    
    -- 平台信息
    platform VARCHAR(20) NOT NULL,
    platform_order_id VARCHAR(100) NOT NULL,
    
    -- 订单信息
    status VARCHAR(20) NOT NULL COMMENT '状态: pending/paid/shipped/delivered/refunded',
    status_text VARCHAR(50) COMMENT '状态描述',
    total_amount DECIMAL(12,2) NOT NULL,
    
    -- 商品信息
    items JSONB NOT NULL COMMENT '商品列表',
    
    -- 物流信息
    logistics_company VARCHAR(50),
    tracking_number VARCHAR(100),
    
    -- 时间
    paid_at TIMESTAMP,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_shop ON orders(shop_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_platform ON orders(platform, platform_order_id);
```

---

## 知识库模块

### KnowledgeCategory (知识库分类)
```sql
CREATE TABLE knowledge_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchants(id),
    parent_id UUID REFERENCES knowledge_categories(id),
    name VARCHAR(100) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### KnowledgeEntry (知识库条目)
```sql
CREATE TABLE knowledge_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchants(id),
    category_id UUID REFERENCES knowledge_categories(id),
    
    question TEXT NOT NULL COMMENT '问题',
    answer TEXT NOT NULL COMMENT '答案',
    
    -- 扩展匹配
    similar_questions JSONB DEFAULT '[]' COMMENT '相似问题',
    keywords JSONB DEFAULT '[]' COMMENT '关键词',
    
    -- 使用统计
    use_count INTEGER DEFAULT 0,
    
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_knowledge_merchant ON knowledge_entries(merchant_id);
CREATE INDEX idx_knowledge_category ON knowledge_entries(category_id);
```

---

## 统计模块

### DailyStats (每日统计)
```sql
CREATE TABLE daily_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shops(id),
    date DATE NOT NULL,
    
    -- 对话统计
    conversation_count INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    ai_handled_count INTEGER DEFAULT 0,
    human_handled_count INTEGER DEFAULT 0,
    
    -- 响应时间
    avg_response_time INTEGER COMMENT '平均响应时间(秒)',
    
    -- 满意度
    satisfaction_score DECIMAL(3,2),
    
    -- 订单统计
    order_count INTEGER DEFAULT 0,
    sales_amount DECIMAL(12,2) DEFAULT 0,
    
    UNIQUE(shop_id, date)
);

CREATE INDEX idx_daily_stats_shop_date ON daily_stats(shop_id, date);
```

### HourlyStats (小时统计)
```sql
CREATE TABLE hourly_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shops(id),
    hour INTEGER NOT NULL CHECK (hour >= 0 AND hour <= 23),
    
    conversation_count INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(shop_id, hour)
);
```

---

## 索引汇总

### 性能优化索引
```sql
-- 会话查询优化
CREATE INDEX idx_conversations_active ON conversations(shop_id, status) WHERE status = 'active';
CREATE INDEX idx_conversations_ai_status ON conversations(shop_id, ai_status);

-- 消息查询优化
CREATE INDEX idx_messages_unread ON messages(conversation_id, is_read) WHERE is_read = FALSE;

-- 客户查询优化
CREATE INDEX idx_customers_spent ON customers(merchant_id, total_spent DESC);

-- 订单查询优化
CREATE INDEX idx_orders_recent ON orders(shop_id, created_at DESC);
```

---

## 数据迁移脚本

### 初始化数据
```sql
-- 创建默认商家
INSERT INTO merchants (name, owner_id) VALUES 
('默认商家', (SELECT id FROM users WHERE username = 'admin'));

-- 创建示例店铺
INSERT INTO shops (merchant_id, name, platform, platform_shop_id, status) VALUES
((SELECT id FROM merchants LIMIT 1), '示例淘宝店铺', 'taobao', 'TB123456', 'active'),
((SELECT id FROM merchants LIMIT 1), '示例京东店铺', 'jd', 'JD654321', 'active');
```
