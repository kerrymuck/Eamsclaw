"""
京东平台适配器
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import json
from .base import PlatformAdapter, UnifiedMessage, UnifiedOrder, MessageType, SenderType, OrderItem
from .registry import PlatformMeta


class JDAdapter(PlatformAdapter, metaclass=PlatformMeta):
    """
    京东平台适配器
    支持京东自营和POP店铺
    """
    
    platform_id = "jd"
    platform_name = "京东"
    platform_type = "b2c"
    platform_category = "domestic"
    
    # 京东API配置
    API_BASE_URL = "https://api.jd.com/routerjson"
    AUTH_URL = "https://open.jd.com/oauth2/authorize"
    TOKEN_URL = "https://open.jd.com/oauth2/access_token"
    
    def __init__(self, app_key: str = None, app_secret: str = None):
        super().__init__(app_key, app_secret)
        self.api_version = "2.0"
    
    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """生成京东API签名"""
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
        """京东OAuth授权"""
        params = {
            "grant_type": "authorization_code",
            "client_id": self.app_key,
            "client_secret": self.app_secret,
            "code": auth_code,
            "redirect_uri": "https://your-app.com/callback"
        }
        
        # TODO: 实际调用京东授权接口
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(self.TOKEN_URL, data=params) as resp:
        #         result = await resp.json()
        
        return {
            "access_token": "jd_mock_token",
            "refresh_token": "jd_mock_refresh",
            "expire_in": 86400,
            "shop_info": {
                "shop_id": "JD123456",
                "shop_name": "京东示例店铺",
                "shop_type": "pop"  # pop 或 self
            }
        }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新令牌"""
        params = {
            "grant_type": "refresh_token",
            "client_id": self.app_key,
            "client_secret": self.app_secret,
            "refresh_token": refresh_token
        }
        
        # TODO: 实际调用刷新接口
        return {
            "access_token": "jd_new_mock_token",
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
        """发送京东咚咚消息"""
        # 京东咚咚消息API: jingdong.im.sendMsg
        params = {
            "method": "jingdong.im.sendMsg",
            "access_token": self.access_token,
            "v": self.api_version,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "360buy_param_json": json.dumps({
                "pin": customer_id,
                "content": content,
                "shopId": shop_id
            })
        }
        params["sign"] = self._generate_sign(params)
        
        print(f"[JD] 发送咚咚消息到 {customer_id}: {content}")
        # TODO: 实际API调用
        return True
    
    async def get_messages(
        self, 
        shop_id: str, 
        conversation_id: str, 
        **kwargs
    ) -> List[UnifiedMessage]:
        """获取消息列表"""
        # 京东消息查询API: jingdong.im.getHistory
        params = {
            "method": "jingdong.im.getHistory",
            "access_token": self.access_token,
            "v": self.api_version,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "360buy_param_json": json.dumps({
                "shopId": shop_id,
                "buyerPin": conversation_id,
                "page": kwargs.get("page", 1),
                "pageSize": kwargs.get("page_size", 20)
            })
        }
        params["sign"] = self._generate_sign(params)
        
        # TODO: 解析返回结果并转换为UnifiedMessage
        return []
    
    async def get_order(self, shop_id: str, order_id: str) -> UnifiedOrder:
        """获取订单详情"""
        # 京东订单查询API: jingdong.order.getOrderInfo
        params = {
            "method": "jingdong.order.getOrderInfo",
            "access_token": self.access_token,
            "v": self.api_version,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "360buy_param_json": json.dumps({
                "orderId": order_id
            })
        }
        params["sign"] = self._generate_sign(params)
        
        # TODO: 解析返回结果
        return UnifiedOrder(
            id=f"jd_{order_id}",
            platform="jd",
            platform_order_id=order_id,
            platform_shop_id=shop_id,
            customer_id="jd_customer_xxx",
            status="wait_seller_send_goods",
            status_text="等待出库",
            currency="CNY",
            total_amount=2999.00,
            items=[],
            created_at=datetime.now()
        )
    
    async def get_orders(
        self, 
        shop_id: str, 
        **kwargs
    ) -> List[UnifiedOrder]:
        """获取订单列表"""
        # 京东订单搜索API: jingdong.order.search
        params = {
            "method": "jingdong.order.search",
            "access_token": self.access_token,
            "v": self.api_version,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "360buy_param_json": json.dumps({
                "startDate": kwargs.get("start_date", ""),
                "endDate": kwargs.get("end_date", ""),
                "orderState": kwargs.get("status", ""),
                "page": kwargs.get("page", 1),
                "pageSize": kwargs.get("page_size", 20)
            })
        }
        params["sign"] = self._generate_sign(params)
        
        # TODO: 解析返回结果
        return []
    
    async def get_customer(self, shop_id: str, customer_id: str) -> Dict[str, Any]:
        """获取客户信息"""
        # 京东客户信息API
        return {
            "customer_id": customer_id,
            "name": "京东用户",
            "avatar": "",
            "level": "金牌会员",
            "credit": 100
        }
    
    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[UnifiedMessage]:
        """解析京东Webhook消息"""
        msg_type = payload.get("type")
        
        if msg_type == "im_message":
            # 咚咚消息
            msg_data = payload.get("data", {})
            return UnifiedMessage(
                id=msg_data.get("msgId", ""),
                platform="jd",
                platform_shop_id=msg_data.get("shopId", ""),
                platform_message_id=msg_data.get("msgId"),
                conversation_id=msg_data.get("buyerPin", ""),
                customer_id=msg_data.get("buyerPin", ""),
                customer_name=msg_data.get("buyerName", ""),
                message_type=MessageType.TEXT,
                content=msg_data.get("content", ""),
                sender_type=SenderType.CUSTOMER if msg_data.get("fromBuyer") else SenderType.AGENT,
                created_at=datetime.fromtimestamp(msg_data.get("timestamp", 0) / 1000)
            )
        elif msg_type == "order":
            # 订单变更消息，不处理（返回None）
            return None
            
        return None
    
    def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """验证Webhook签名"""
        # 京东Webhook签名验证逻辑
        expected_sign = hashlib.md5(
            f"{self.app_secret}{json.dumps(payload, sort_keys=True)}{self.app_secret}".encode()
        ).hexdigest().upper()
        return expected_sign == signature
    
    async def get_logistics(
        self, 
        shop_id: str, 
        tracking_number: str
    ) -> Dict[str, Any]:
        """查询京东物流信息"""
        # 京东物流查询API: jingdong.etms.trace.get
        params = {
            "method": "jingdong.etms.trace.get",
            "access_token": self.access_token,
            "v": self.api_version,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "360buy_param_json": json.dumps({
                "waybillCode": tracking_number
            })
        }
        params["sign"] = self._generate_sign(params)
        
        # TODO: 解析返回结果
        return {
            "tracking_number": tracking_number,
            "company": "京东快递",
            "status": "运输中",
            "traces": []
        }
