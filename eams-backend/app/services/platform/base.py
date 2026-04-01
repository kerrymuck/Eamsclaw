"""
EAMS 平台适配器基类
支持国内及跨境主流电商平台
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class MessageType(str, Enum):
    """消息类型"""
    TEXT = "text"
    IMAGE = "image"
    PRODUCT = "product"
    ORDER = "order"
    SYSTEM = "system"


class SenderType(str, Enum):
    """发送者类型"""
    CUSTOMER = "customer"
    AGENT = "agent"
    AI = "ai"
    SYSTEM = "system"


class UnifiedMessage(BaseModel):
    """统一消息格式"""
    id: str
    platform: str
    platform_shop_id: str
    platform_message_id: Optional[str] = None
    
    conversation_id: str
    customer_id: str
    customer_name: Optional[str] = None
    customer_avatar: Optional[str] = None
    
    message_type: MessageType = MessageType.TEXT
    content: str
    content_extra: Optional[Dict[str, Any]] = None
    
    sender_type: SenderType
    sender_id: Optional[str] = None
    sender_name: Optional[str] = None
    
    created_at: datetime
    platform_created_at: Optional[datetime] = None
    
    metadata: Optional[Dict[str, Any]] = None


class OrderItem(BaseModel):
    """订单商品项"""
    product_id: Optional[str] = None
    sku_id: Optional[str] = None
    title: str
    image: Optional[str] = None
    price: float
    quantity: int
    total: float


class UnifiedOrder(BaseModel):
    """统一订单格式"""
    id: str
    platform: str
    platform_order_id: str
    platform_shop_id: str
    
    customer_id: str
    customer_name: Optional[str] = None
    
    status: str
    status_text: str
    
    currency: str = "CNY"
    total_amount: float
    subtotal: Optional[float] = None
    shipping_fee: Optional[float] = None
    discount: Optional[float] = None
    
    items: List[OrderItem] = []
    
    logistics_company: Optional[str] = None
    tracking_number: Optional[str] = None
    
    created_at: datetime
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    platform_metadata: Optional[Dict[str, Any]] = None


class PlatformAdapter(ABC):
    """
    平台适配器基类
    所有电商平台适配器必须继承此类并实现所有抽象方法
    """
    
    # 平台标识（必须唯一）
    platform_id: str = ""
    platform_name: str = ""
    platform_type: str = ""  # b2c/b2b/c2c/social/independent
    platform_category: str = ""  # domestic/crossborder
    
    def __init__(self, app_key: str = None, app_secret: str = None):
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = None
        self.refresh_token = None
    
    @abstractmethod
    async def authenticate(self, auth_code: str) -> Dict[str, Any]:
        """
        OAuth授权 - 获取access_token
        
        Args:
            auth_code: 授权码
            
        Returns:
            {
                "access_token": "xxx",
                "refresh_token": "xxx",
                "expire_in": 3600,
                "shop_info": {...}
            }
        """
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        刷新令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            {
                "access_token": "xxx",
                "refresh_token": "xxx",
                "expire_in": 3600
            }
        """
        pass
    
    @abstractmethod
    async def send_message(
        self, 
        shop_id: str, 
        customer_id: str, 
        content: str, 
        **kwargs
    ) -> bool:
        """
        发送消息给客户
        
        Args:
            shop_id: 店铺ID
            customer_id: 客户ID
            content: 消息内容
            **kwargs: 额外参数
            
        Returns:
            是否发送成功
        """
        pass
    
    @abstractmethod
    async def get_messages(
        self, 
        shop_id: str, 
        conversation_id: str, 
        **kwargs
    ) -> List[UnifiedMessage]:
        """
        获取消息列表
        
        Args:
            shop_id: 店铺ID
            conversation_id: 会话ID
            **kwargs: 额外参数（如分页）
            
        Returns:
            消息列表
        """
        pass
    
    @abstractmethod
    async def get_order(self, shop_id: str, order_id: str) -> UnifiedOrder:
        """
        获取订单详情
        
        Args:
            shop_id: 店铺ID
            order_id: 订单ID
            
        Returns:
            订单信息
        """
        pass
    
    @abstractmethod
    async def get_orders(
        self, 
        shop_id: str, 
        **kwargs
    ) -> List[UnifiedOrder]:
        """
        获取订单列表
        
        Args:
            shop_id: 店铺ID
            **kwargs: 额外参数（如状态、时间范围）
            
        Returns:
            订单列表
        """
        pass
    
    @abstractmethod
    async def get_customer(self, shop_id: str, customer_id: str) -> Dict[str, Any]:
        """
        获取客户信息
        
        Args:
            shop_id: 店铺ID
            customer_id: 客户ID
            
        Returns:
            客户信息
        """
        pass
    
    @abstractmethod
    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[UnifiedMessage]:
        """
        解析Webhook消息为统一格式
        
        Args:
            payload: Webhook原始数据
            
        Returns:
            统一格式的消息，如果不是消息事件则返回None
        """
        pass
    
    @abstractmethod
    def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """
        验证Webhook签名
        
        Args:
            payload: Webhook数据
            signature: 签名
            
        Returns:
            签名是否有效
        """
        pass
    
    async def get_shop_info(self, access_token: str) -> Dict[str, Any]:
        """
        获取店铺信息（可选实现）
        
        Args:
            access_token: 访问令牌
            
        Returns:
            店铺信息
        """
        return {}
    
    async def get_products(
        self, 
        shop_id: str, 
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        获取商品列表（可选实现）
        
        Args:
            shop_id: 店铺ID
            **kwargs: 额外参数
            
        Returns:
            商品列表
        """
        return []
    
    async def get_logistics(
        self, 
        shop_id: str, 
        tracking_number: str
    ) -> Dict[str, Any]:
        """
        查询物流信息（可选实现）
        
        Args:
            shop_id: 店铺ID
            tracking_number: 物流单号
            
        Returns:
            物流信息
        """
        return {}
