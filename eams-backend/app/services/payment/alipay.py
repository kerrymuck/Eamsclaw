"""
支付宝支付集成
"""

import os
import json
import base64
from datetime import datetime
from typing import Dict, Optional

try:
    from alipay import AliPay
except ImportError:
    # 尝试其他导入方式
    try:
        from alipay.aop.api import AlipayClientConfig, DefaultAlipayClient
        AliPay = None
    except ImportError:
        AliPay = None


class AlipayService:
    """支付宝支付服务"""
    
    def __init__(self):
        self.app_id = os.getenv("ALIPAY_APP_ID")
        self.private_key = os.getenv("ALIPAY_PRIVATE_KEY")
        self.alipay_public_key = os.getenv("ALIPAY_PUBLIC_KEY")
        self.gateway = os.getenv("ALIPAY_GATEWAY", "https://openapi.alipay.com/gateway.do")
        
        self.alipay = None
        if AliPay and self.app_id and self.private_key:
            try:
                self.alipay = AliPay(
                    appid=self.app_id,
                    app_notify_url=os.getenv("ALIPAY_NOTIFY_URL", ""),
                    app_private_key_string=self._format_key(self.private_key, "private"),
                    alipay_public_key_string=self._format_key(self.alipay_public_key, "public") if self.alipay_public_key else None,
                    sign_type="RSA2",
                    debug=False
                )
            except Exception as e:
                print(f"支付宝初始化失败: {e}")
    
    def _format_key(self, key: str, key_type: str) -> str:
        """格式化密钥"""
        if not key:
            return ""
        
        # 如果已经包含BEGIN/END，直接返回
        if "BEGIN" in key:
            return key
        
        # 添加BEGIN/END
        if key_type == "private":
            return f"-----BEGIN RSA PRIVATE KEY-----\n{key}\n-----END RSA PRIVATE KEY-----"
        else:
            return f"-----BEGIN PUBLIC KEY-----\n{key}\n-----END PUBLIC KEY-----"
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return AliPay is not None and self.alipay is not None
    
    def create_order(
        self,
        order_no: str,
        amount: float,
        subject: str = "AI算力充值",
        return_url: Optional[str] = None
    ) -> Dict:
        """
        创建支付宝订单
        
        Returns:
            {
                "order_string": "...",  # 用于调起支付宝APP或跳转
                "payment_url": "..."    # 支付页面URL
            }
        """
        if not self.alipay:
            raise ValueError("支付宝未配置")
        
        # 创建订单
        order_string = self.alipay.api_alipay_trade_page_pay(
            out_trade_no=order_no,
            total_amount=str(amount),
            subject=subject,
            return_url=return_url or "",
            notify_url=os.getenv("ALIPAY_NOTIFY_URL", "")
        )
        
        # 构建支付URL
        payment_url = f"{self.gateway}?{order_string}"
        
        return {
            "order_string": order_string,
            "payment_url": payment_url
        }
    
    def verify_notify(self, data: Dict) -> bool:
        """验证支付回调"""
        if not self.alipay:
            return False
        
        signature = data.pop("sign", None)
        return self.alipay.verify(data, signature)
    
    def query_order(self, order_no: str) -> Dict:
        """查询订单状态"""
        if not self.alipay:
            raise ValueError("支付宝未配置")
        
        result = self.alipay.api_alipay_trade_query(out_trade_no=order_no)
        return result


# 全局实例
_alipay_service = None


def get_alipay_service() -> AlipayService:
    """获取支付宝服务单例"""
    global _alipay_service
    if _alipay_service is None:
        _alipay_service = AlipayService()
    return _alipay_service
