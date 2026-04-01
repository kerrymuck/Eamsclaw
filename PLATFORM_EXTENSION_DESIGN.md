# EAMS 跨境电商平台支持清单

## 主流跨境电商平台

### B2C平台

| 平台 | 平台ID | 所属公司 | 主要市场 | 图标 | 主色调 |
|------|--------|----------|----------|------|--------|
| Amazon | amazon | Amazon | 全球 | 🅰️ | #ff9900 |
| eBay | ebay | eBay | 全球 | 🛒 | #e53238 |
| AliExpress | aliexpress | 阿里巴巴 | 全球 | 🌍 | #ff4747 |
| Shopee | shopee | Sea | 东南亚/拉美 | 🧡 | #ee4d2d |
| Lazada | lazada | 阿里巴巴 | 东南亚 | 💙 | #0f156d |
| Temu | temu | 拼多多 | 北美/欧洲 | 🛍️ | #fb7701 |
| TikTok Shop | tiktokshop | ByteDance | 全球 | 🎵 | #000000 |
| Wish | wish | ContextLogic | 北美/欧洲 | ⭐ | #2fb7ec |
| SHEIN | shein | 希音 | 全球 | 👗 | #000000 |
| Mercado Libre | mercadolibre | MercadoLibre | 拉美 | 🌎 | #ffe600 |
| Rakuten | rakuten | 乐天 | 日本 | 🎌 | #bf0000 |
| Coupang | coupang | Coupang | 韩国 | 🇰🇷 | #00a0e9 |
| Ozon | ozon | Ozon | 俄罗斯 | 🇷🇺 | #0066cc |
| Joom | joom | Joom | 欧洲 | 📦 | #0096f2 |
| Allegro | allegro | Allegro | 波兰/欧洲 | 🇵🇱 | #ff5a00 |

### B2B平台

| 平台 | 平台ID | 所属公司 | 主要市场 | 图标 | 主色调 |
|------|--------|----------|----------|------|--------|
| Alibaba.com | alibaba | 阿里巴巴 | 全球 | 🔶 | #ff6a00 |
| Made-in-China | madeinchina | 焦点科技 | 全球 | 🇨🇳 | #c41230 |
| Global Sources | globalsources | 环球资源 | 全球 | 🌐 | #004b8d |
| DHgate | dhgate | 敦煌网 | 全球 | 🏛️ | #ff6a00 |

### 独立站平台

| 平台 | 平台ID | 类型 | 图标 | 主色调 |
|------|--------|------|------|--------|
| Shopify | shopify | SaaS建站 | 🛍️ | #96bf48 |
| WooCommerce | woocommerce | WordPress插件 | 🌐 | #96588a |
| BigCommerce | bigcommerce | SaaS建站 | 🅱️ | #34313f |
| Magento | magento | 开源 | 🅼️ | #f26322 |

---

## 平台分类

### 按地区分类
- **北美**: Amazon, eBay, Walmart, Wish, Temu, SHEIN
- **欧洲**: Amazon EU, eBay EU, Allegro, Zalando, Otto, Joom
- **东南亚**: Shopee, Lazada, Tokopedia, Bukalapak
- **拉美**: Mercado Libre, Amazon Brazil, Shopee Brazil
- **中东**: Noon, Amazon UAE, Trendyol
- **俄罗斯**: Ozon, Wildberries
- **日本**: Rakuten, Amazon Japan, Yahoo Shopping
- **韩国**: Coupang, Gmarket, 11st

### 按模式分类
- **B2C**: Amazon, eBay, AliExpress, Shopee, Lazada, Temu, TikTok Shop
- **B2B**: Alibaba.com, Made-in-China, Global Sources, DHgate
- **C2C**: eBay, Mercado Libre
- **社交电商**: TikTok Shop, Facebook Shops, Instagram Shopping
- **独立站**: Shopify, WooCommerce, BigCommerce

---

## 后端可扩展架构设计

### 平台适配器工厂模式

```python
# app/services/platform/base.py
from abc import ABC, abstractmethod
from typing import Dict, Type

class PlatformAdapter(ABC):
    """平台适配器基类 - 所有平台必须实现"""
    
    platform_id: str = ""  # 平台标识
    platform_name: str = ""  # 平台名称
    platform_type: str = ""  # 平台类型: b2c/b2b/c2c/social
    
    @abstractmethod
    async def authenticate(self, auth_code: str) -> Dict:
        """OAuth授权 - 获取access_token"""
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Dict:
        """刷新令牌"""
        pass
    
    @abstractmethod
    async def send_message(self, shop_id: str, customer_id: str, content: str, **kwargs) -> bool:
        """发送消息给客户"""
        pass
    
    @abstractmethod
    async def get_messages(self, shop_id: str, conversation_id: str, **kwargs) -> list:
        """获取消息列表"""
        pass
    
    @abstractmethod
    async def get_order(self, shop_id: str, order_id: str) -> Dict:
        """获取订单详情"""
        pass
    
    @abstractmethod
    async def get_orders(self, shop_id: str, **kwargs) -> list:
        """获取订单列表"""
        pass
    
    @abstractmethod
    async def get_customer(self, shop_id: str, customer_id: str) -> Dict:
        """获取客户信息"""
        pass
    
    @abstractmethod
    def parse_webhook(self, payload: Dict) -> Dict:
        """解析Webhook消息为统一格式"""
        pass
    
    @abstractmethod
    def verify_webhook(self, payload: Dict, signature: str) -> bool:
        """验证Webhook签名"""
        pass


# 平台适配器注册表 - 动态加载
class PlatformAdapterRegistry:
    """平台适配器注册表 - 支持动态扩展"""
    
    _adapters: Dict[str, Type[PlatformAdapter]] = {}
    _platform_info: Dict[str, Dict] = {}
    
    @classmethod
    def register(cls, adapter_class: Type[PlatformAdapter]):
        """注册平台适配器"""
        platform_id = adapter_class.platform_id
        cls._adapters[platform_id] = adapter_class
        cls._platform_info[platform_id] = {
            'id': platform_id,
            'name': adapter_class.platform_name,
            'type': adapter_class.platform_type,
        }
        print(f"✅ 注册平台适配器: {platform_id}")
    
    @classmethod
    def get_adapter(cls, platform_id: str) -> PlatformAdapter:
        """获取平台适配器实例"""
        adapter_class = cls._adapters.get(platform_id)
        if not adapter_class:
            raise ValueError(f"未找到平台适配器: {platform_id}")
        return adapter_class()
    
    @classmethod
    def list_platforms(cls) -> list:
        """列出所有支持的平台"""
        return list(cls._platform_info.values())
    
    @classmethod
    def is_supported(cls, platform_id: str) -> bool:
        """检查平台是否支持"""
        return platform_id in cls._adapters


# 装饰器自动注册
class PlatformMeta(type):
    """元类 - 自动注册平台适配器"""
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        # 排除基类本身
        if name != 'PlatformAdapter' and hasattr(cls, 'platform_id') and cls.platform_id:
            PlatformAdapterRegistry.register(cls)
        return cls


# 更新基类使用元类
class PlatformAdapter(ABC, metaclass=PlatformMeta):
    """平台适配器基类 - 所有平台必须实现"""
    platform_id: str = ""
    platform_name: str = ""
    platform_type: str = ""
    # ... 其他方法
```

### 具体平台适配器实现示例

```python
# app/services/platform/amazon.py
class AmazonAdapter(PlatformAdapter):
    """Amazon平台适配器"""
    
    platform_id = "amazon"
    platform_name = "Amazon"
    platform_type = "b2c"
    
    # Amazon SP-API配置
    AWS_ACCESS_KEY = ""
    AWS_SECRET_KEY = ""
    LWA_APP_ID = ""
    LWA_CLIENT_SECRET = ""
    
    async def authenticate(self, auth_code: str) -> Dict:
        """Amazon OAuth授权"""
        # 调用Amazon LWA授权接口
        pass
    
    async def send_message(self, shop_id: str, customer_id: str, content: str, **kwargs) -> bool:
        """Amazon买家-卖家消息"""
        # 调用Amazon Messaging API
        pass
    
    async def get_order(self, shop_id: str, order_id: str) -> Dict:
        """获取Amazon订单"""
        # 调用Amazon Orders API
        pass
    
    def parse_webhook(self, payload: Dict) -> Dict:
        """解析Amazon SQS消息"""
        # 转换为统一格式
        pass


# app/services/platform/shopee.py
class ShopeeAdapter(PlatformAdapter):
    """Shopee平台适配器"""
    
    platform_id = "shopee"
    platform_name = "Shopee"
    platform_type = "b2c"
    
    async def authenticate(self, auth_code: str) -> Dict:
        """Shopee授权"""
        pass
    
    async def send_message(self, shop_id: str, customer_id: str, content: str, **kwargs) -> bool:
        """Shopee聊天消息"""
        pass


# app/services/platform/tiktokshop.py
class TikTokShopAdapter(PlatformAdapter):
    """TikTok Shop平台适配器"""
    
    platform_id = "tiktokshop"
    platform_name = "TikTok Shop"
    platform_type = "social"
    
    async def authenticate(self, auth_code: str) -> Dict:
        """TikTok Shop授权"""
        pass
```

### 动态加载适配器

```python
# app/services/platform/__init__.py
import os
import importlib
from pathlib import Path

def load_adapters():
    """动态加载所有平台适配器"""
    adapter_dir = Path(__file__).parent
    
    # 遍历所有适配器文件
    for file in adapter_dir.glob("*.py"):
        if file.stem not in ["__init__", "base"]:
            # 动态导入模块，触发元类注册
            importlib.import_module(f"app.services.platform.{file.stem}")
    
    print(f"✅ 共加载 {len(PlatformAdapterRegistry._adapters)} 个平台适配器")

# 启动时加载
load_adapters()
```

### 统一消息格式

```python
# app/models/message.py
from enum import Enum
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PlatformType(str, Enum):
    """平台类型"""
    DOMESTIC = "domestic"      # 国内电商
    CROSSBORDER = "crossborder"  # 跨境电商
    B2B = "b2b"               # B2B平台
    SOCIAL = "social"         # 社交电商
    INDEPENDENT = "independent"  # 独立站

class MessageType(str, Enum):
    """消息类型"""
    TEXT = "text"
    IMAGE = "image"
    PRODUCT = "product"
    ORDER = "order"
    SYSTEM = "system"

class UnifiedMessage(BaseModel):
    """统一消息格式 - 所有平台消息转换为此格式"""
    
    # 消息标识
    id: str
    platform: str                    # 平台ID: taobao/amazon/shopee/...
    platform_shop_id: str            # 平台店铺ID
    platform_message_id: Optional[str] = None  # 平台消息ID
    
    # 会话信息
    conversation_id: str
    customer_id: str
    customer_name: Optional[str] = None
    customer_avatar: Optional[str] = None
    
    # 消息内容
    type: MessageType = MessageType.TEXT
    content: str
    content_extra: Optional[Dict] = None  # 额外内容（图片URL、商品信息等）
    
    # 发送者
    sender_type: str                  # customer/agent/ai/system
    sender_id: Optional[str] = None
    sender_name: Optional[str] = None
    
    # 时间戳
    created_at: datetime
    platform_created_at: Optional[datetime] = None
    
    # 元数据
    metadata: Optional[Dict] = None   # 平台特定元数据
    
    class Config:
        from_attributes = True


class UnifiedOrder(BaseModel):
    """统一订单格式"""
    
    id: str
    platform: str
    platform_order_id: str
    platform_shop_id: str
    
    # 客户信息
    customer_id: str
    customer_name: Optional[str] = None
    
    # 订单状态
    status: str                       # pending/paid/shipped/delivered/refunded
    status_text: str                  # 平台状态描述
    
    # 金额
    currency: str = "CNY"
    total_amount: float
    subtotal: Optional[float] = None
    shipping_fee: Optional[float] = None
    discount: Optional[float] = None
    
    # 商品
    items: List[OrderItem]
    
    # 物流
    logistics_company: Optional[str] = None
    tracking_number: Optional[str] = None
    
    # 时间
    created_at: datetime
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    # 平台元数据
    platform_metadata: Optional[Dict] = None


class OrderItem(BaseModel):
    """订单商品项"""
    product_id: Optional[str] = None
    sku_id: Optional[str] = None
    title: str
    image: Optional[str] = None
    price: float
    quantity: int
    total: float
```

### 平台配置表

```sql
-- 平台配置表 - 支持动态扩展
CREATE TABLE platform_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_id VARCHAR(50) NOT NULL UNIQUE,  -- 平台标识: amazon/shopee/...
    platform_name VARCHAR(100) NOT NULL,       -- 平台名称
    platform_type VARCHAR(20) NOT NULL,        -- 类型: b2c/b2b/social/...
    platform_category VARCHAR(20) NOT NULL,    -- 分类: domestic/crossborder
    
    -- 平台特性
    features JSONB DEFAULT '[]',               -- 支持的功能列表
    auth_type VARCHAR(20) DEFAULT 'oauth',     -- 授权类型: oauth/apikey/...
    auth_config JSONB DEFAULT '{}',            -- 授权配置
    
    -- API配置
    api_base_url VARCHAR(500),
    api_version VARCHAR(20),
    api_config JSONB DEFAULT '{}',             -- API端点配置
    
    -- Webhook配置
    webhook_supported BOOLEAN DEFAULT FALSE,
    webhook_config JSONB DEFAULT '{}',         -- Webhook配置
    
    -- 状态
    is_active BOOLEAN DEFAULT TRUE,
    is_beta BOOLEAN DEFAULT FALSE,             -- 是否Beta版本
    
    -- 排序
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入平台配置
INSERT INTO platform_configs (platform_id, platform_name, platform_type, platform_category, features, is_active) VALUES
-- 国内平台
('taobao', '淘宝', 'b2c', 'domestic', '["message", "order", "product"]', true),
('tmall', '天猫', 'b2c', 'domestic', '["message", "order", "product"]', true),
('jd', '京东', 'b2c', 'domestic', '["message", "order", "product"]', true),
('pdd', '拼多多', 'b2c', 'domestic', '["message", "order", "product"]', true),
('douyin', '抖店', 'social', 'domestic', '["message", "order", "product"]', true),
('xiaohongshu', '小红书', 'social', 'domestic', '["message", "order"]', true),
('alibaba', '1688', 'b2b', 'domestic', '["message", "order"]', true),

-- 跨境平台
('amazon', 'Amazon', 'b2c', 'crossborder', '["message", "order", "product"]', true),
('ebay', 'eBay', 'c2c', 'crossborder', '["message", "order"]', true),
('aliexpress', '速卖通', 'b2c', 'crossborder', '["message", "order", "product"]', true),
('shopee', 'Shopee', 'b2c', 'crossborder', '["message", "order", "product"]', true),
('lazada', 'Lazada', 'b2c', 'crossborder', '["message", "order", "product"]', true),
('temu', 'Temu', 'b2c', 'crossborder', '["order"]', true),
('tiktokshop', 'TikTok Shop', 'social', 'crossborder', '["message", "order", "product"]', true),
('shein', 'SHEIN', 'b2c', 'crossborder', '["order"]', true),
('mercadolibre', 'Mercado Libre', 'b2c', 'crossborder', '["message", "order"]', true),
('rakuten', 'Rakuten', 'b2c', 'crossborder', '["message", "order"]', true),
('coupang', 'Coupang', 'b2c', 'crossborder', '["message", "order"]', true),
('ozon', 'Ozon', 'b2c', 'crossborder', '["message", "order"]', true),

-- 独立站
('shopify', 'Shopify', 'independent', 'crossborder', '["order"]', true),
('woocommerce', 'WooCommerce', 'independent', 'crossborder', '["order"]', true);
```

### API路由设计

```python
# app/api/v1/platform.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter()

@router.get("/platforms")
async def list_platforms():
    """获取所有支持的平台列表"""
    return PlatformAdapterRegistry.list_platforms()

@router.get("/platforms/{platform_id}/auth-url")
async def get_auth_url(platform_id: str):
    """获取平台授权链接"""
    adapter = PlatformAdapterRegistry.get_adapter(platform_id)
    # 生成授权URL
    return {"auth_url": auth_url}

@router.post("/platforms/{platform_id}/callback")
async def auth_callback(platform_id: str, code: str):
    """平台授权回调"""
    adapter = PlatformAdapterRegistry.get_adapter(platform_id)
    result = await adapter.authenticate(code)
    return result

@router.post("/platforms/{platform_id}/webhook")
async def platform_webhook(platform_id: str, request: Request):
    """接收平台Webhook消息"""
    adapter = PlatformAdapterRegistry.get_adapter(platform_id)
    payload = await request.json()
    
    # 验证签名
    signature = request.headers.get("X-Signature")
    if not adapter.verify_webhook(payload, signature):
        raise HTTPException(401, "Invalid signature")
    
    # 解析为统一格式
    message = adapter.parse_webhook(payload)
    
    # 处理消息
    await process_message(message)
    
    return {"status": "ok"}
```

---

## 扩展新平台步骤

1. **创建适配器文件** `app/services/platform/{platform_id}.py`
2. **继承PlatformAdapter基类**
3. **实现所有抽象方法**
4. **自动注册到系统**（通过元类）
5. **配置平台参数** 到 `platform_configs` 表
6. **前端添加平台图标和配置**

无需修改核心业务代码，新平台自动接入！
