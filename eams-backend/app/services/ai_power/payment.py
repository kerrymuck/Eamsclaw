"""
支付服务 - 充值订单处理、支付回调
"""

import logging
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Optional

from app.models.ai_power import RechargeOrder, AIAccount, AITransaction
from app.services.ai_power.billing import BillingService
from app.services.payment.alipay import get_alipay_service
from app.services.payment.wechat import get_wechat_service
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class PaymentService:
    """支付服务"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.billing = BillingService()
    
    async def create_recharge_order(
        self,
        shop_id: str,
        amount: Decimal,
        payment_method: str
    ) -> Dict:
        """
        创建充值订单
        
        Args:
            shop_id: 商户ID
            amount: 充值金额
            payment_method: 支付方式（alipay/wechat）
            
        Returns:
            {
                "order_no": "...",
                "amount": 金额,
                "payment_url": "支付跳转URL",
                "expire_at": "过期时间"
            }
        """
        # 生成订单号
        order_no = f"AI{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
        
        # 创建订单
        order = RechargeOrder(
            shop_id=shop_id,
            order_no=order_no,
            amount=amount,
            payment_method=payment_method,
            status='pending'
        )
        
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        # 获取支付URL
        payment_url = await self._get_payment_url(order)
        
        logger.info(f"创建充值订单: order_no={order_no}, amount={amount}, method={payment_method}")
        
        return {
            "order_no": order_no,
            "amount": float(amount),
            "payment_url": payment_url,
            "expire_at": (datetime.utcnow() + timedelta(hours=2)).isoformat()
        }
    
    async def _get_payment_url(self, order: RechargeOrder) -> str:
        """获取支付跳转URL"""
        if order.payment_method == 'alipay':
            alipay = get_alipay_service()
            if alipay.is_configured():
                try:
                    result = alipay.create_order(
                        order_no=order.order_no,
                        amount=float(order.amount),
                        subject="AI算力充值"
                    )
                    return result["payment_url"]
                except Exception as e:
                    logger.error(f"支付宝创建订单失败: {e}")
                    # 降级到模拟支付
                    return f"/payment/alipay/mock?order_no={order.order_no}"
            else:
                # 支付宝未配置，使用模拟支付
                return f"/payment/alipay/mock?order_no={order.order_no}"
        
        elif order.payment_method == 'wechat':
            wechat = get_wechat_service()
            if wechat.is_configured():
                try:
                    result = wechat.create_order(
                        order_no=order.order_no,
                        amount=float(order.amount),
                        description="AI算力充值"
                    )
                    # 返回扫码支付URL
                    return result.get("code_url", f"/payment/wechat/mock?order_no={order.order_no}")
                except Exception as e:
                    logger.error(f"微信创建订单失败: {e}")
                    return f"/payment/wechat/mock?order_no={order.order_no}"
            else:
                return f"/payment/wechat/mock?order_no={order.order_no}"
        
        else:
            raise ValueError(f"不支持的支付方式: {order.payment_method}")
    
    async def handle_payment_notify(
        self,
        payment_method: str,
        notify_data: Dict
    ) -> bool:
        """
        处理支付回调
        
        Args:
            payment_method: 支付方式
            notify_data: 回调数据
            
        Returns:
            是否处理成功
        """
        try:
            # 验证签名（TODO: 实际验证）
            # if not self._verify_signature(payment_method, notify_data):
            #     logger.error("支付回调签名验证失败")
            #     return False
            
            # 获取订单号
            order_no = notify_data.get('out_trade_no') or notify_data.get('order_no')
            if not order_no:
                logger.error("支付回调缺少订单号")
                return False
            
            # 查询订单
            order = self.db.query(RechargeOrder).filter(
                RechargeOrder.order_no == order_no
            ).first()
            
            if not order:
                logger.error(f"订单不存在: {order_no}")
                return False
            
            if order.status == 'paid':
                logger.warning(f"订单已支付: {order_no}")
                return True
            
            if order.status != 'pending':
                logger.error(f"订单状态错误: {order_no}, status={order.status}")
                return False
            
            # 更新订单状态
            order.status = 'paid'
            order.paid_at = datetime.utcnow()
            order.transaction_no = notify_data.get('trade_no') or notify_data.get('transaction_id')
            order.notify_data = notify_data
            order.notified_at = datetime.utcnow()
            
            self.db.commit()
            
            # 充值到账
            await self.billing.recharge(
                shop_id=str(order.shop_id),
                amount=order.amount,
                order_id=str(order.id),
                payment_method=payment_method
            )
            
            logger.info(f"支付回调处理成功: order_no={order_no}, amount={order.amount}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"支付回调处理失败: {e}", exc_info=True)
            return False
    
    async def query_order_status(self, order_no: str) -> Dict:
        """查询订单状态"""
        order = self.db.query(RechargeOrder).filter(
            RechargeOrder.order_no == order_no
        ).first()
        
        if not order:
            raise ValueError(f"订单不存在: {order_no}")
        
        return {
            "order_no": order.order_no,
            "amount": float(order.amount),
            "status": order.status,
            "payment_method": order.payment_method,
            "paid_at": order.paid_at.isoformat() if order.paid_at else None,
            "created_at": order.created_at.isoformat()
        }
    
    async def get_recharge_records(
        self,
        shop_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """获取充值记录"""
        query = self.db.query(RechargeOrder).filter(
            RechargeOrder.shop_id == shop_id
        )
        
        total = query.count()
        items = query.order_by(
            RechargeOrder.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [
                {
                    "order_no": item.order_no,
                    "amount": float(item.amount),
                    "gift_amount": float(item.gift_amount),
                    "payment_method": item.payment_method,
                    "status": item.status,
                    "paid_at": item.paid_at.isoformat() if item.paid_at else None,
                    "created_at": item.created_at.isoformat()
                }
                for item in items
            ]
        }
    
    def _verify_signature(self, payment_method: str, data: Dict) -> bool:
        """
        验证支付回调签名
        
        TODO: 实现实际签名验证
        """
        # 支付宝验证
        if payment_method == 'alipay':
            # return alipay.verify_sign(data)
            pass
        
        # 微信验证
        elif payment_method == 'wechat':
            # return wechat_pay.verify_sign(data)
            pass
        
        return True  # 临时返回True
