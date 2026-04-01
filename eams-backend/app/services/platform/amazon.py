"""
Amazon平台适配器
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from .base import PlatformAdapter, UnifiedMessage, UnifiedOrder, MessageType, SenderType
from .registry import PlatformMeta


class AmazonAdapter(PlatformAdapter, metaclass=PlatformMeta):
    """
    Amazon平台适配器
    使用Amazon Selling Partner API (SP-API)
    """
    
    platform_id = "amazon"
    platform_name = "Amazon"
    platform_type = "b2c"
    platform_category = "crossborder"
    
    # Amazon API配置
    API_BASE_URL_US = "https://sellingpartnerapi-na.amazon.com"
    API_BASE_URL_EU = "https://sellingpartnerapi-eu.amazon.com"
    API_BASE_URL_FE = "https://sellingpartnerapi-fe.amazon.com"
    
    AUTH_URL = "https://sellercentral.amazon.com/apps/authorize/consent"
    TOKEN_URL = "https://api.amazon.com/auth/o2/token"
    
    # AWS配置
    aws_access_key: str = ""
    aws_secret_key: str = ""
    
    async def authenticate(self, auth_code: str) -> Dict[str, Any]:
        """Amazon OAuth授权 (LWA)"""
        # TODO: 实现Amazon LWA授权
        return {
            "access_token": "mock_amazon_token",
            "refresh_token": "mock_amazon_refresh",
            "expire_in": 3600,
            "shop_info": {
                "shop_id": "A123456789",
                "shop_name": "Amazon Store",
                "marketplace": "US"
            }
        }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新令牌"""
        return {
            "access_token": "new_mock_amazon_token",
            "refresh_token": refresh_token,
            "expire_in": 3600
        }
    
    async def send_message(
        self, 
        shop_id: str, 
        customer_id: str, 
        content: str, 
        **kwargs
    ) -> bool:
        """发送Amazon买家-卖家消息"""
        print(f"[Amazon] 发送消息到 {customer_id}: {content}")
        return True
    
    async def get_messages(
        self, 
        shop_id: str, 
        conversation_id: str, 
        **kwargs
    ) -> List[UnifiedMessage]:
        """获取消息列表"""
        # TODO: 调用Amazon Messaging API
        return []
    
    async def get_order(self, shop_id: str, order_id: str) -> UnifiedOrder:
        """获取订单详情"""
        # TODO: 调用Amazon Orders API
        return UnifiedOrder(
            id="order_xxx",
            platform="amazon",
            platform_order_id=order_id,
            platform_shop_id=shop_id,
            customer_id="cust_xxx",
            status="shipped",
            status_text="Shipped",
            currency="USD",
            total_amount=199.99,
            items=[],
            created_at=datetime.now()
        )
    
    async def get_orders(
        self, 
        shop_id: str, 
        **kwargs
    ) -> List[UnifiedOrder]:
        """获取订单列表"""
        return []
    
    async def get_customer(self, shop_id: str, customer_id: str) -> Dict[str, Any]:
        """获取客户信息"""
        # Amazon不直接提供客户信息，需要脱敏处理
        return {
            "customer_id": customer_id,
            "name": "Amazon Customer",
            "avatar": "",
            "is_anonymous": True
        }
    
    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[UnifiedMessage]:
        """解析Amazon SQS消息"""
        # TODO: 解析Amazon SQS通知
        notification_type = payload.get("NotificationType")
        
        if notification_type == "ORDER_CHANGE":
            return None
        elif notification_type == "BUYER_MESSAGE":
            return UnifiedMessage(
                id=payload.get("MessageId", ""),
                platform="amazon",
                platform_shop_id=payload.get("SellerId", ""),
                conversation_id=payload.get("BuyerId", ""),
                customer_id=payload.get("BuyerId", ""),
                message_type=MessageType.TEXT,
                content=payload.get("Message", ""),
                sender_type=SenderType.CUSTOMER,
                created_at=datetime.now()
            )
        return None
    
    def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """验证Webhook签名"""
        # TODO: 实现AWS签名验证
        return True
