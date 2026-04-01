"""
抖音电商（抖店）平台适配器
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import json
import hmac
import base64
from .base import PlatformAdapter, UnifiedMessage, UnifiedOrder, MessageType, SenderType, OrderItem
from .registry import PlatformMeta


class DouyinAdapter(PlatformAdapter, metaclass=PlatformMeta):
    """
    抖音电商（抖店）平台适配器
    支持抖店客服消息和订单管理
    """
    
    platform_id = "douyin"
    platform_name = "抖店"
    platform_type = "b2c"
    platform_category = "domestic"
    
    # 抖店API配置
    API_BASE_URL = "https://openapi-fxg.jinritemai.com"
    AUTH_URL = "https://openapi-fxg.jinritemai.com/oauth/authorize"
    TOKEN_URL = "https://openapi-fxg.jinritemai.com/oauth/access_token"
    
    def __init__(self, app_key: str = None, app_secret: str = None):
        super().__init__(app_key, app_secret)
        self.api_version = "2"
    
    def _generate_sign(self, params: Dict[str, Any], method: str = "POST") -> str:
        """生成抖店API签名"""
        # 抖店使用HMAC-SHA256签名
        # 1. 按参数名排序
        sorted_params = sorted(params.items())
        # 2. 拼接参数字符串
        param_str = "&".join([f"{k}={v}" for k, v in sorted_params if v is not None])
        # 3. 构造签名字符串
        sign_str = f"{method}&%2F&{self._percent_encode(param_str)}"
        # 4. HMAC-SHA256加密
        sign = hmac.new(
            f"{self.app_secret}&".encode(),
            sign_str.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(sign).decode()
    
    def _percent_encode(self, s: str) -> str:
        """URL编码"""
        from urllib.parse import quote
        return quote(s, safe='')
    
    async def authenticate(self, auth_code: str) -> Dict[str, Any]:
        """抖店OAuth授权"""
        params = {
            "app_id": self.app_key,
            "app_secret": self.app_secret,
            "code": auth_code,
            "grant_type": "authorization_code"
        }
        
        # TODO: 实际调用抖店授权接口
        return {
            "access_token": "douyin_mock_token",
            "refresh_token": "douyin_mock_refresh",
            "expire_in": 86400,
            "shop_info": {
                "shop_id": "DY123456",
                "shop_name": "抖店示例店铺",
                "shop_type": "普通店"
            }
        }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新令牌"""
        params = {
            "app_id": self.app_key,
            "app_secret": self.app_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        return {
            "access_token": "douyin_new_mock_token",
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
        """发送抖店客服消息"""
        # 抖店发送消息API: /message/send
        endpoint = "/message/send"
        params = {
            "app_id": self.app_key,
            "method": endpoint,
            "access_token": self.access_token,
            "v": self.api_version,
            "timestamp": str(int(datetime.now().timestamp())),
            "shop_id": shop_id,
            "buyer_id": customer_id,
            "msg_type": kwargs.get("msg_type", "text"),  # text/image/product/order
            "content": content
        }
        params["sign"] = self._generate_sign(params)
        
        print(f"[Douyin] 发送客服消息到 {customer_id}: {content}")
        return True
    
    async def get_messages(
        self, 
        shop_id: str, 
        conversation_id: str, 
        **kwargs
    ) -> List[UnifiedMessage]:
        """获取消息列表"""
        # 抖店获取消息列表API: /message/list
        endpoint = "/message/list"
        params = {
            "app_id": self.app_key,
            "method": endpoint,
            "access_token": self.access_token,
            "v": self.api_version,
            "timestamp": str(int(datetime.now().timestamp())),
            "shop_id": shop_id,
            "buyer_id": conversation_id,
            "page": kwargs.get("page", 1),
            "size": kwargs.get("page_size", 20)
        }
        params["sign"] = self._generate_sign(params)
        
        return []
    
    async def get_order(self, shop_id: str, order_id: str) -> UnifiedOrder:
        """获取订单详情"""
        # 抖店订单详情API: /order/detail
        endpoint = "/order/detail"
        params = {
            "app_id": self.app_key,
            "method": endpoint,
            "access_token": self.access_token,
            "v": self.api_version,
            "timestamp": str(int(datetime.now().timestamp())),
            "shop_order_id": order_id
        }
        params["sign"] = self._generate_sign(params)
        
        return UnifiedOrder(
            id=f"douyin_{order_id}",
            platform="douyin",
            platform_order_id=order_id,
            platform_shop_id=shop_id,
            customer_id="douyin_customer_xxx",
            status="待发货",
            status_text="待发货",
            currency="CNY",
            total_amount=599.00,
            items=[],
            created_at=datetime.now()
        )
    
    async def get_orders(
        self, 
        shop_id: str, 
        **kwargs
    ) -> List[UnifiedOrder]:
        """获取订单列表"""
        # 抖店订单搜索API: /order/searchList
        endpoint = "/order/searchList"
        params = {
            "app_id": self.app_key,
            "method": endpoint,
            "access_token": self.access_token,
            "v": self.api_version,
            "timestamp": str(int(datetime.now().timestamp())),
            "shop_id": shop_id,
            "order_status": kwargs.get("status", ""),  # 1-待确认 2-待发货 3-已发货 4-已签收
            "start_time": kwargs.get("start_time", ""),
            "end_time": kwargs.get("end_time", ""),
            "page": kwargs.get("page", 1),
            "size": kwargs.get("page_size", 20)
        }
        params["sign"] = self._generate_sign(params)
        
        return []
    
    async def get_customer(self, shop_id: str, customer_id: str) -> Dict[str, Any]:
        """获取客户信息"""
        return {
            "customer_id": customer_id,
            "name": "抖音用户",
            "avatar": "",
            "level": "普通用户",
            "follow_status": "已关注"
        }
    
    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[UnifiedMessage]:
        """解析抖店Webhook消息"""
        event_type = payload.get("event_type")
        
        if event_type == "MsgCreate":
            # 新消息事件
            msg_data = payload.get("data", {})
            return UnifiedMessage(
                id=msg_data.get("msg_id", ""),
                platform="douyin",
                platform_shop_id=msg_data.get("shop_id", ""),
                platform_message_id=msg_data.get("msg_id"),
                conversation_id=msg_data.get("buyer_id", ""),
                customer_id=msg_data.get("buyer_id", ""),
                customer_name=msg_data.get("buyer_name", ""),
                message_type=MessageType.TEXT if msg_data.get("msg_type") == "text" else MessageType.IMAGE,
                content=msg_data.get("content", ""),
                sender_type=SenderType.CUSTOMER if msg_data.get("is_buyer") else SenderType.AGENT,
                created_at=datetime.fromtimestamp(msg_data.get("create_time", 0))
            )
        elif event_type == "TradeCreate":
            # 新订单事件
            return None
        elif event_type == "TradePaid":
            # 订单支付事件
            return None
            
        return None
    
    def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """验证Webhook签名"""
        # 抖店Webhook签名验证
        sign_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        expected_sign = hmac.new(
            self.app_secret.encode(),
            sign_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return expected_sign == signature
    
    async def get_products(
        self, 
        shop_id: str, 
        **kwargs
    ) -> List[Dict[str, Any]]:
        """获取商品列表"""
        # 抖店商品列表API: /product/list
        endpoint = "/product/list"
        params = {
            "app_id": self.app_key,
            "method": endpoint,
            "access_token": self.access_token,
            "v": self.api_version,
            "timestamp": str(int(datetime.now().timestamp())),
            "shop_id": shop_id,
            "page": kwargs.get("page", 1),
            "size": kwargs.get("page_size", 20),
            "status": kwargs.get("status", 0)  # 0-全部 1-上架 2-下架
        }
        params["sign"] = self._generate_sign(params)
        
        return []


class DouyinLiveAdapter(DouyinAdapter):
    """
    抖音直播电商适配器
    继承抖店适配器，添加直播相关功能
    """
    
    platform_id = "douyin_live"
    platform_name = "抖音直播"
    platform_type = "b2c"
    platform_category = "domestic"
    
    async def get_live_rooms(self, shop_id: str) -> List[Dict[str, Any]]:
        """获取直播间列表"""
        # 抖店直播间列表API
        return []
    
    async def get_live_products(self, shop_id: str, room_id: str) -> List[Dict[str, Any]]:
        """获取直播间商品"""
        # 抖店直播间商品API
        return []
