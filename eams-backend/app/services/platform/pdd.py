"""
拼多多平台适配器
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import json
import time
from .base import PlatformAdapter, UnifiedMessage, UnifiedOrder, MessageType, SenderType, OrderItem
from .registry import PlatformMeta


class PddAdapter(PlatformAdapter, metaclass=PlatformMeta):
    """
    拼多多平台适配器
    支持拼多多店铺消息和订单管理
    """
    
    platform_id = "pdd"
    platform_name = "拼多多"
    platform_type = "c2c"
    platform_category = "domestic"
    
    # 拼多多API配置
    API_BASE_URL = "https://gw-api.pinduoduo.com/api/router"
    AUTH_URL = "https://open.pinduoduo.com/oauth/authorize"
    TOKEN_URL = "https://open.pinduoduo.com/oauth/token"
    
    def __init__(self, app_key: str = None, app_secret: str = None):
        super().__init__(app_key, app_secret)
        self.data_type = "JSON"
    
    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """生成拼多多API签名"""
        # 按参数名排序
        sorted_params = sorted(params.items())
        # 拼接字符串
        sign_str = self.app_secret
        for key, value in sorted_params:
            if key != "sign" and value is not None:
                sign_str += f"{key}{value}"
        sign_str += self.app_secret
        # MD5加密
        return hashlib.md5(sign_str.encode()).hexdigest().upper()
    
    async def authenticate(self, auth_code: str) -> Dict[str, Any]:
        """拼多多OAuth授权"""
        params = {
            "type": "pdd.pop.auth.token.create",
            "client_id": self.app_key,
            "client_secret": self.app_secret,
            "code": auth_code,
            "grant_type": "authorization_code"
        }
        params["sign"] = self._generate_sign(params)
        
        # TODO: 实际调用拼多多授权接口
        return {
            "access_token": "pdd_mock_token",
            "refresh_token": "pdd_mock_refresh",
            "expire_in": 86400,
            "shop_info": {
                "shop_id": "PDD123456",
                "shop_name": "拼多多示例店铺",
                "mall_id": "12345678"
            }
        }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新令牌"""
        params = {
            "type": "pdd.pop.auth.token.refresh",
            "client_id": self.app_key,
            "client_secret": self.app_secret,
            "refresh_token": refresh_token
        }
        params["sign"] = self._generate_sign(params)
        
        return {
            "access_token": "pdd_new_mock_token",
            "refresh_token": refresh_token,
            "expire_in": 86400
        }
    
    async def send_message(
        self, 
        shop_id: str, 
        customer_id: str, 
        content: str, 
        **kwargs
    ) -> bool:
        """发送拼多多客服消息"""
        # 拼多多发送消息API: pdd.logistics.cs.message.send
        params = {
            "type": "pdd.logistics.cs.message.send",
            "client_id": self.app_key,
            "access_token": self.access_token,
            "timestamp": str(int(time.time())),
            "data_type": self.data_type,
            "owner_id": shop_id,
            "msg_type": kwargs.get("msg_type", "text"),  # text/image/goods/order
            "content": content,
            "buyer_id": customer_id
        }
        params["sign"] = self._generate_sign(params)
        
        print(f"[PDD] 发送客服消息到 {customer_id}: {content}")
        return True
    
    async def get_messages(
        self, 
        shop_id: str, 
        conversation_id: str, 
        **kwargs
    ) -> List[UnifiedMessage]:
        """获取消息列表"""
        # 拼多多获取会话列表API: pdd.logistics.cs.session.list.get
        params = {
            "type": "pdd.logistics.cs.session.list.get",
            "client_id": self.app_key,
            "access_token": self.access_token,
            "timestamp": str(int(time.time())),
            "data_type": self.data_type,
            "owner_id": shop_id,
            "session_id": conversation_id,
            "page": kwargs.get("page", 1),
            "page_size": kwargs.get("page_size", 20)
        }
        params["sign"] = self._generate_sign(params)
        
        return []
    
    async def get_order(self, shop_id: str, order_id: str) -> UnifiedOrder:
        """获取订单详情"""
        # 拼多多订单详情API: pdd.order.information.get
        params = {
            "type": "pdd.order.information.get",
            "client_id": self.app_key,
            "access_token": self.access_token,
            "timestamp": str(int(time.time())),
            "data_type": self.data_type,
            "order_sn": order_id
        }
        params["sign"] = self._generate_sign(params)
        
        return UnifiedOrder(
            id=f"pdd_{order_id}",
            platform="pdd",
            platform_order_id=order_id,
            platform_shop_id=shop_id,
            customer_id="pdd_customer_xxx",
            status="待发货",
            status_text="待发货",
            currency="CNY",
            total_amount=199.00,
            items=[],
            created_at=datetime.now()
        )
    
    async def get_orders(
        self, 
        shop_id: str, 
        **kwargs
    ) -> List[UnifiedOrder]:
        """获取订单列表"""
        # 拼多多订单列表API: pdd.order.number.list.get
        params = {
            "type": "pdd.order.number.list.get",
            "client_id": self.app_key,
            "access_token": self.access_token,
            "timestamp": str(int(time.time())),
            "data_type": self.data_type,
            "order_status": kwargs.get("status", 1),  # 1-待发货 2-待收货 3-已签收
            "page": kwargs.get("page", 1),
            "page_size": kwargs.get("page_size", 20),
            "start_confirm_at": kwargs.get("start_time", ""),
            "end_confirm_at": kwargs.get("end_time", "")
        }
        params["sign"] = self._generate_sign(params)
        
        return []
    
    async def get_customer(self, shop_id: str, customer_id: str) -> Dict[str, Any]:
        """获取客户信息"""
        return {
            "customer_id": customer_id,
            "name": "拼多多用户",
            "avatar": "",
            "level": "普通会员"
        }
    
    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[UnifiedMessage]:
        """解析拼多多Webhook消息"""
        msg_type = payload.get("type")
        
        if msg_type == "pdd.logistics.cs.message.notify":
            # 客服消息通知
            msg_data = payload.get("message", {})
            return UnifiedMessage(
                id=msg_data.get("id", ""),
                platform="pdd",
                platform_shop_id=msg_data.get("mall_id", ""),
                platform_message_id=msg_data.get("msg_id"),
                conversation_id=msg_data.get("session_id", ""),
                customer_id=msg_data.get("buyer_id", ""),
                customer_name=msg_data.get("buyer_name", ""),
                message_type=MessageType.TEXT if msg_data.get("msg_type") == "text" else MessageType.IMAGE,
                content=msg_data.get("content", ""),
                sender_type=SenderType.CUSTOMER if msg_data.get("from_buyer") else SenderType.AGENT,
                created_at=datetime.fromtimestamp(msg_data.get("timestamp", 0))
            )
        elif msg_type == "pdd.trade.order.notify":
            # 订单通知
            return None
            
        return None
    
    def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """验证Webhook签名"""
        expected_sign = hashlib.md5(
            f"{self.app_secret}{json.dumps(payload, sort_keys=True)}{self.app_secret}".encode()
        ).hexdigest().upper()
        return expected_sign == signature


class PddMallAdapter(PddAdapter):
    """
    拼多多店铺（Mall）适配器
    与普通店铺使用相同接口
    """
    
    platform_id = "pdd_mall"
    platform_name = "拼多多店铺"
    platform_type = "b2c"
    platform_category = "domestic"
