"""
淘宝/天猫平台适配器
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from .base import PlatformAdapter, UnifiedMessage, UnifiedOrder, MessageType, SenderType
from .registry import PlatformMeta


class TaobaoAdapter(PlatformAdapter, metaclass=PlatformMeta):
    """
    淘宝/天猫平台适配器
    支持淘宝和天猫两个平台
    """
    
    platform_id = "taobao"
    platform_name = "淘宝"
    platform_type = "b2c"
    platform_category = "domestic"
    
    # 淘宝API配置
    API_BASE_URL = "https://eco.taobao.com/router/rest"
    AUTH_URL = "https://oauth.taobao.com/authorize"
    TOKEN_URL = "https://oauth.taobao.com/token"
    
    async def authenticate(self, auth_code: str) -> Dict[str, Any]:
        """淘宝OAuth授权"""
        # TODO: 实现淘宝OAuth授权
        # 调用淘宝开放平台接口获取access_token
        return {
            "access_token": "mock_token",
            "refresh_token": "mock_refresh",
            "expire_in": 3600,
            "shop_info": {
                "shop_id": "TB123456",
                "shop_name": "示例店铺"
            }
        }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新令牌"""
        # TODO: 实现刷新令牌
        return {
            "access_token": "new_mock_token",
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
        """发送旺旺消息"""
        # TODO: 调用淘宝消息接口
        print(f"[Taobao] 发送消息到 {customer_id}: {content}")
        return True
    
    async def get_messages(
        self, 
        shop_id: str, 
        conversation_id: str, 
        **kwargs
    ) -> List[UnifiedMessage]:
        """获取消息列表"""
        # TODO: 调用淘宝消息查询接口
        return []
    
    async def get_order(self, shop_id: str, order_id: str) -> UnifiedOrder:
        """获取订单详情"""
        # TODO: 调用淘宝订单接口
        return UnifiedOrder(
            id="order_xxx",
            platform="taobao",
            platform_order_id=order_id,
            platform_shop_id=shop_id,
            customer_id="cust_xxx",
            status="paid",
            status_text="买家已付款",
            total_amount=9999.00,
            items=[],
            created_at=datetime.now()
        )
    
    async def get_orders(
        self, 
        shop_id: str, 
        **kwargs
    ) -> List[UnifiedOrder]:
        """获取订单列表"""
        # TODO: 调用淘宝订单列表接口
        return []
    
    async def get_customer(self, shop_id: str, customer_id: str) -> Dict[str, Any]:
        """获取客户信息"""
        # TODO: 调用淘宝客户接口
        return {
            "customer_id": customer_id,
            "name": "淘宝用户",
            "avatar": ""
        }
    
    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[UnifiedMessage]:
        """解析淘宝Webhook消息"""
        # TODO: 解析淘宝消息推送
        msg_type = payload.get("msg_type")
        
        if msg_type == "TradeChanged":
            # 订单变更消息
            return None
        elif msg_type == "WangwangMessage":
            # 旺旺消息
            return UnifiedMessage(
                id=payload.get("id", ""),
                platform="taobao",
                platform_shop_id=payload.get("shop_id", ""),
                conversation_id=payload.get("buyer_id", ""),
                customer_id=payload.get("buyer_id", ""),
                customer_name=payload.get("buyer_name", ""),
                message_type=MessageType.TEXT,
                content=payload.get("content", ""),
                sender_type=SenderType.CUSTOMER,
                created_at=datetime.now()
            )
        return None
    
    def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """验证Webhook签名"""
        # TODO: 实现签名验证
        return True


class TmallAdapter(TaobaoAdapter):
    """
    天猫平台适配器
    继承淘宝适配器，大部分接口相同
    """
    
    platform_id = "tmall"
    platform_name = "天猫"
    platform_type = "b2c"
    platform_category = "domestic"
