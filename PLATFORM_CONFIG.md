# EAMS 电商平台对接配置

## 支持平台列表

### 国内电商平台

| 平台 | 平台ID | 图标 | 主色调 | 开放平台 |
|------|--------|------|--------|----------|
| 淘宝 | taobao | 🍑 | #ff5000 | 千牛开放平台 |
| 天猫 | tmall | 🐱 | #ff0036 | 千牛开放平台 |
| 1688 | alibaba | 🔶 | #ff6a00 | 1688开放平台 |
| 京东 | jd | 🐕 | #e4393c | 宙斯开放平台 |
| 拼多多 | pdd | 🟥 | #e02e24 | 拼多多开放平台 |
| 抖店 | douyin | 🎵 | #000000 | 抖店开放平台 |
| 小红书 | xiaohongshu | 📕 | #ff2442 | 小红书开放平台 |

### 跨境电商平台

| 平台 | 平台ID | 图标 | 主色调 | 开放平台 |
|------|--------|------|--------|----------|
| 速卖通 | aliexpress | 🌍 | #ff4747 | 速卖通开放平台 |

---

## 平台对接配置

### 1. 淘宝/天猫 (Taobao/Tmall)

**开放平台**: [千牛开放平台](https://open.taobao.com/)

**配置参数**:
```env
TAOBAO_APP_KEY=your_app_key
TAOBAO_APP_SECRET=your_app_secret
TAOBAO_CALLBACK_URL=https://your-domain.com/api/v1/platform/taobao/callback
```

**权限申请**:
- 用户消息读取
- 订单信息查询
- 商品信息查询
- 物流信息查询
- 客服消息发送

**Webhook事件**:
- `TradeChanged` - 订单变更
- `ItemChanged` - 商品变更
- `WangwangMessage` - 旺旺消息

---

### 2. 京东 (JD)

**开放平台**: [宙斯开放平台](https://open.jd.com/)

**配置参数**:
```env
JD_APP_KEY=your_app_key
JD_APP_SECRET=your_app_secret
JD_CALLBACK_URL=https://your-domain.com/api/v1/platform/jd/callback
```

**权限申请**:
- 订单查询接口
- 消息推送服务
- 商品信息查询
- 售后服务接口

**Webhook事件**:
- `order_notification` - 订单通知
- `message_notification` - 消息通知

---

### 3. 拼多多 (PDD)

**开放平台**: [拼多多开放平台](https://open.pinduoduo.com/)

**配置参数**:
```env
PDD_APP_KEY=your_app_key
PDD_APP_SECRET=your_app_secret
PDD_CALLBACK_URL=https://your-domain.com/api/v1/platform/pdd/callback
```

**权限申请**:
- 订单数据接口
- 消息推送服务
- 售后数据接口

**Webhook事件**:
- `TRADE_CHANGED` - 订单变更
- `MESSAGE` - 消息推送

---

### 4. 抖店 (Douyin)

**开放平台**: [抖店开放平台](https://op.jinritemai.com/)

**配置参数**:
```env
DOUYIN_APP_KEY=your_app_key
DOUYIN_APP_SECRET=your_app_secret
DOUYIN_CALLBACK_URL=https://your-domain.com/api/v1/platform/douyin/callback
```

**权限申请**:
- 订单管理
- 消息推送
- 售后管理

**Webhook事件**:
- `order` - 订单事件
- `message` - 消息事件

---

### 5. 小红书 (Xiaohongshu)

**开放平台**: [小红书开放平台](https://open.xiaohongshu.com/)

**配置参数**:
```env
XIAOHONGSHU_APP_KEY=your_app_key
XIAOHONGSHU_APP_SECRET=your_app_secret
XIAOHONGSHU_CALLBACK_URL=https://your-domain.com/api/v1/platform/xiaohongshu/callback
```

**权限申请**:
- 订单接口
- 消息接口

---

### 6. 1688 (Alibaba B2B)

**开放平台**: [1688开放平台](https://open.1688.com/)

**配置参数**:
```env
ALIBABA_APP_KEY=your_app_key
ALIBABA_APP_SECRET=your_app_secret
ALIBABA_CALLBACK_URL=https://your-domain.com/api/v1/platform/alibaba/callback
```

---

### 7. 速卖通 (AliExpress)

**开放平台**: [速卖通开放平台](https://developers.aliexpress.com/)

**配置参数**:
```env
ALIEXPRESS_APP_KEY=your_app_key
ALIEXPRESS_APP_SECRET=your_app_secret
ALIEXPRESS_CALLBACK_URL=https://your-domain.com/api/v1/platform/aliexpress/callback
```

**权限申请**:
- 订单查询
- 消息服务
- 物流跟踪

---

## 统一消息格式

所有平台的消息都将转换为统一格式：

```json
{
  "platform": "taobao",
  "platform_shop_id": "TB123456",
  "event_type": "message",
  "data": {
    "conversation_id": "conv_xxx",
    "customer_id": "cust_xxx",
    "customer_name": "张先生",
    "message_id": "msg_xxx",
    "content": "什么时候发货？",
    "content_type": "text",
    "created_at": "2024-03-21T10:30:00Z"
  }
}
```

---

## 统一订单格式

```json
{
  "platform": "taobao",
  "platform_order_id": "TB202403210001",
  "shop_id": "shop_xxx",
  "customer_id": "cust_xxx",
  "status": "shipped",
  "status_text": "已发货",
  "total_amount": 9999.00,
  "items": [
    {
      "product_id": "prod_xxx",
      "title": "iPhone 15 Pro Max",
      "price": 9999.00,
      "quantity": 1,
      "image": "https://..."
    }
  ],
  "logistics": {
    "company": "顺丰速运",
    "tracking_number": "SF1234567890"
  },
  "created_at": "2024-03-21T10:00:00Z",
  "paid_at": "2024-03-21T10:05:00Z",
  "shipped_at": "2024-03-21T14:00:00Z"
}
```

---

## 平台适配器设计

```python
# app/services/platform/base.py
from abc import ABC, abstractmethod

class PlatformAdapter(ABC):
    """平台适配器基类"""
    
    @abstractmethod
    async def authenticate(self, auth_code: str) -> dict:
        """平台授权"""
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> dict:
        """刷新令牌"""
        pass
    
    @abstractmethod
    async def send_message(self, shop_id: str, customer_id: str, content: str) -> bool:
        """发送消息"""
        pass
    
    @abstractmethod
    async def get_order(self, shop_id: str, order_id: str) -> dict:
        """获取订单"""
        pass
    
    @abstractmethod
    async def get_orders(self, shop_id: str, **kwargs) -> list:
        """获取订单列表"""
        pass
    
    @abstractmethod
    def parse_webhook(self, payload: dict) -> dict:
        """解析Webhook消息"""
        pass

# app/services/platform/taobao.py
class TaobaoAdapter(PlatformAdapter):
    """淘宝适配器"""
    
    async def authenticate(self, auth_code: str) -> dict:
        # 调用淘宝OAuth接口
        pass
    
    async def send_message(self, shop_id: str, customer_id: str, content: str) -> bool:
        # 调用淘宝消息接口
        pass
    
    def parse_webhook(self, payload: dict) -> dict:
        # 解析淘宝Webhook
        pass

# app/services/platform/jd.py
class JDAdapter(PlatformAdapter):
    """京东适配器"""
    pass

# app/services/platform/pdd.py
class PDDAdapter(PlatformAdapter):
    """拼多多适配器"""
    pass

# 适配器工厂
class PlatformAdapterFactory:
    _adapters = {
        'taobao': TaobaoAdapter,
        'tmall': TaobaoAdapter,  # 天猫使用淘宝适配器
        'jd': JDAdapter,
        'pdd': PDDAdapter,
        'douyin': DouyinAdapter,
        'xiaohongshu': XiaohongshuAdapter,
        'alibaba': AlibabaAdapter,
        'aliexpress': AliexpressAdapter,
    }
    
    @classmethod
    def get_adapter(cls, platform: str) -> PlatformAdapter:
        adapter_class = cls._adapters.get(platform)
        if not adapter_class:
            raise ValueError(f"不支持的平台: {platform}")
        return adapter_class()
```

---

## 数据库表更新

### 店铺表增加平台字段

```sql
-- 店铺表已支持的平台列表
ALTER TABLE shops ADD CONSTRAINT valid_platform 
CHECK (platform IN ('taobao', 'tmall', 'alibaba', 'aliexpress', 'jd', 'pdd', 'douyin', 'xiaohongshu'));
```

---

## 前端平台配置

```typescript
// config/platforms.ts
export const PLATFORMS = {
  // 阿里系
  taobao: { name: '淘宝', icon: '🍑', color: '#ff5000', category: 'domestic' },
  tmall: { name: '天猫', icon: '🐱', color: '#ff0036', category: 'domestic' },
  alibaba: { name: '1688', icon: '🔶', color: '#ff6a00', category: 'b2b' },
  aliexpress: { name: '速卖通', icon: '🌍', color: '#ff4747', category: 'crossborder' },
  
  // 其他国内平台
  jd: { name: '京东', icon: '🐕', color: '#e4393c', category: 'domestic' },
  pdd: { name: '拼多多', icon: '🟥', color: '#e02e24', category: 'domestic' },
  douyin: { name: '抖店', icon: '🎵', color: '#000000', category: 'domestic' },
  xiaohongshu: { name: '小红书', icon: '📕', color: '#ff2442', category: 'domestic' },
} as const;

export type PlatformType = keyof typeof PLATFORMS;
```

---

## 注意事项

1. **授权有效期**: 不同平台的授权有效期不同，需要定时刷新
2. **频率限制**: 各平台API都有调用频率限制，需要做好限流
3. **消息推送**: 需要配置稳定的Webhook接收服务
4. **数据安全**: 平台敏感信息需要加密存储
5. **合规性**: 遵守各平台的数据使用规范
