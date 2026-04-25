"""
微信支付集成
"""

import os
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Optional
import requests


class WechatPayService:
    """微信支付服务"""
    
    def __init__(self):
        self.mch_id = os.getenv("WECHAT_MCH_ID")
        self.api_key = os.getenv("WECHAT_API_KEY")
        self.cert_path = os.getenv("WECHAT_CERT_PATH")
        self.key_path = os.getenv("WECHAT_KEY_PATH")
        self.notify_url = os.getenv("WECHAT_NOTIFY_URL", "")
        
        self.gateway = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.mch_id and self.api_key)
    
    def _generate_nonce_str(self, length: int = 32) -> str:
        """生成随机字符串"""
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _sign(self, params: Dict) -> str:
        """生成签名"""
        # 按参数名ASCII码排序
        sorted_params = sorted(params.items())
        # 拼接成字符串
        string_a = "&".join([f"{k}={v}" for k, v in sorted_params if v])
        # 拼接API密钥
        string_sign_temp = f"{string_a}&key={self.api_key}"
        # MD5加密并转大写
        return hashlib.md5(string_sign_temp.encode()).hexdigest().upper()
    
    def create_order(
        self,
        order_no: str,
        amount: float,  # 单位：元
        description: str = "AI算力充值",
        client_ip: Optional[str] = None
    ) -> Dict:
        """
        创建微信订单
        
        Returns:
            {
                "prepay_id": "...",
                "pay_sign": "...",
                "app_id": "...",
                "time_stamp": "...",
                "nonce_str": "..."
            }
        """
        if not self.is_configured():
            raise ValueError("微信支付未配置")
        
        params = {
            "appid": os.getenv("WECHAT_APP_ID", ""),  # 需要公众号/小程序APPID
            "mch_id": self.mch_id,
            "nonce_str": self._generate_nonce_str(),
            "body": description,
            "out_trade_no": order_no,
            "total_fee": int(amount * 100),  # 转换为分
            "spbill_create_ip": client_ip or "127.0.0.1",
            "notify_url": self.notify_url,
            "trade_type": "NATIVE"  # 扫码支付
        }
        
        # 生成签名
        params["sign"] = self._sign(params)
        
        # 发送请求
        xml_data = self._dict_to_xml(params)
        response = requests.post(self.gateway, data=xml_data.encode())
        
        # 解析响应
        result = self._xml_to_dict(response.content)
        
        if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
            return {
                "prepay_id": result.get("prepay_id"),
                "code_url": result.get("code_url"),  # 扫码支付URL
                "order_no": order_no
            }
        else:
            raise Exception(f"创建订单失败: {result.get('err_code_des')}")
    
    def _dict_to_xml(self, data: Dict) -> str:
        """字典转XML"""
        xml = ["<xml>"]
        for k, v in data.items():
            xml.append(f"<{k}><![CDATA[{v}]]></{k}>")
        xml.append("</xml>")
        return "".join(xml)
    
    def _xml_to_dict(self, xml_data: bytes) -> Dict:
        """XML转字典"""
        root = ET.fromstring(xml_data)
        return {child.tag: child.text for child in root}
    
    def verify_notify(self, xml_data: bytes) -> Dict:
        """验证支付回调"""
        data = self._xml_to_dict(xml_data)
        
        # 验证签名
        sign = data.pop("sign", "")
        calculated_sign = self._sign(data)
        
        if sign != calculated_sign:
            return {"verified": False}
        
        return {"verified": True, "data": data}
    
    def query_order(self, order_no: str) -> Dict:
        """查询订单状态"""
        if not self.is_configured():
            raise ValueError("微信支付未配置")
        
        params = {
            "appid": os.getenv("WECHAT_APP_ID", ""),
            "mch_id": self.mch_id,
            "out_trade_no": order_no,
            "nonce_str": self._generate_nonce_str()
        }
        params["sign"] = self._sign(params)
        
        xml_data = self._dict_to_xml(params)
        response = requests.post(
            "https://api.mch.weixin.qq.com/pay/orderquery",
            data=xml_data.encode()
        )
        
        return self._xml_to_dict(response.content)


# 全局实例
_wechat_service = None


def get_wechat_service() -> WechatPayService:
    """获取微信支付服务单例"""
    global _wechat_service
    if _wechat_service is None:
        _wechat_service = WechatPayService()
    return _wechat_service
