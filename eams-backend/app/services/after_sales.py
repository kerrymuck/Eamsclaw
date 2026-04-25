"""
售后处理服务 - 自动处理退款/退货/换货申请
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.services.intent_recognition import get_intent_recognizer, BuyerIntent
from app.services.smart_customer_service import get_smart_customer_service

logger = logging.getLogger(__name__)


class AfterSalesService:
    """售后处理服务"""
    
    # 售后类型
    AFTER_SALES_TYPES = {
        "refund": "退款",
        "return": "退货退款",
        "exchange": "换货",
        "repair": "维修",
        "complaint": "投诉"
    }
    
    # 处理策略
    PROCESS_STRATEGIES = {
        "auto_approve": "自动同意",
        "manual_review": "人工审核",
        "reject": "拒绝",
        "negotiate": "协商"
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.intent_recognizer = get_intent_recognizer()
        self.smart_service = get_smart_customer_service(db)
    
    async def analyze_after_sales_request(
        self,
        shop_id: str,
        buyer_id: str,
        request_content: str,
        order_info: Optional[Dict] = None
    ) -> Dict:
        """
        分析售后申请
        
        Args:
            shop_id: 商户ID
            buyer_id: 买家ID
            request_content: 申请内容
            order_info: 订单信息
            
        Returns:
            {
                "type": "refund/return/exchange",
                "urgency": "high/medium/low",
                "sentiment": "negative/neutral",
                "suggested_strategy": "auto_approve/manual_review",
                "reason": "申请原因",
                "confidence": 0.85
            }
        """
        # 意图识别
        intent, confidence = self.intent_recognizer.recognize(request_content)
        
        # 映射到售后类型
        type_mapping = {
            BuyerIntent.REFUND: "refund",
            BuyerIntent.RETURN: "return",
            BuyerIntent.EXCHANGE: "exchange",
            BuyerIntent.COMPLAINT: "complaint",
            BuyerIntent.AFTER_SALES: "repair"
        }
        
        after_sales_type = type_mapping.get(intent, "unknown")
        
        # 分析紧急程度
        urgency = "medium"
        if "急" in request_content or "马上" in request_content:
            urgency = "high"
        
        # 分析情感
        from app.services.sentiment_analysis import get_sentiment_analyzer
        sentiment_analyzer = get_sentiment_analyzer()
        sentiment = sentiment_analyzer.analyze(request_content)
        
        # 确定处理策略
        if after_sales_type == "refund" and order_info:
            # 未发货订单，自动同意退款
            if order_info.get("status") == "unshipped":
                strategy = "auto_approve"
            # 金额较小的订单，自动同意
            elif order_info.get("amount", 0) < 100:
                strategy = "auto_approve"
            else:
                strategy = "manual_review"
        elif after_sales_type == "complaint":
            strategy = "manual_review"
        else:
            strategy = "manual_review"
        
        return {
            "type": after_sales_type,
            "urgency": urgency,
            "sentiment": sentiment["sentiment"],
            "suggested_strategy": strategy,
            "reason": request_content,
            "confidence": confidence
        }
    
    async def process_refund(
        self,
        shop_id: str,
        buyer_id: str,
        order_id: str,
        reason: str,
        amount: Optional[float] = None
    ) -> Dict:
        """
        处理退款申请
        
        Args:
            shop_id: 商户ID
            buyer_id: 买家ID
            order_id: 订单ID
            reason: 退款原因
            amount: 退款金额（None表示全额）
            
        Returns:
            处理结果
        """
        # TODO: 获取订单信息
        order_info = {
            "order_id": order_id,
            "status": "unshipped",  # unshipped/shipped/delivered
            "amount": 299.00,
            "product_name": "示例商品"
        }
        
        # 分析申请
        analysis = await self.analyze_after_sales_request(
            shop_id=shop_id,
            buyer_id=buyer_id,
            request_content=reason,
            order_info=order_info
        )
        
        # 根据策略处理
        if analysis["suggested_strategy"] == "auto_approve":
            # 自动同意退款
            result = await self._auto_approve_refund(
                shop_id=shop_id,
                buyer_id=buyer_id,
                order_id=order_id,
                amount=amount or order_info["amount"],
                reason=reason
            )
        else:
            # 转人工审核
            result = await self._transfer_to_manual(
                shop_id=shop_id,
                buyer_id=buyer_id,
                order_id=order_id,
                after_sales_type="refund",
                reason=reason
            )
        
        return {
            "success": True,
            "order_id": order_id,
            "type": "refund",
            "strategy": analysis["suggested_strategy"],
            "result": result,
            "message": result.get("message", "")
        }
    
    async def process_return(
        self,
        self_service,
        shop_id: str,
        buyer_id: str,
        order_id: str,
        reason: str,
        product_status: str = "unused"  # unused/used/damaged
    ) -> Dict:
        """处理退货申请"""
        # 退货通常需要人工审核
        result = await self._transfer_to_manual(
            shop_id=shop_id,
            buyer_id=buyer_id,
            order_id=order_id,
            after_sales_type="return",
            reason=reason
        )
        
        # 同时发送自动回复
        reply = await self._generate_after_sales_reply(
            shop_id=shop_id,
            buyer_id=buyer_id,
            after_sales_type="return",
            status="processing"
        )
        
        return {
            "success": True,
            "order_id": order_id,
            "type": "return",
            "strategy": "manual_review",
            "result": result,
            "auto_reply": reply
        }
    
    async def process_exchange(
        self,
        shop_id: str,
        buyer_id: str,
        order_id: str,
        reason: str,
        exchange_spec: Optional[str] = None
    ) -> Dict:
        """处理换货申请"""
        result = await self._transfer_to_manual(
            shop_id=shop_id,
            buyer_id=buyer_id,
            order_id=order_id,
            after_sales_type="exchange",
            reason=reason
        )
        
        reply = await self._generate_after_sales_reply(
            shop_id=shop_id,
            buyer_id=buyer_id,
            after_sales_type="exchange",
            status="processing"
        )
        
        return {
            "success": True,
            "order_id": order_id,
            "type": "exchange",
            "strategy": "manual_review",
            "result": result,
            "auto_reply": reply
        }
    
    async def _auto_approve_refund(
        self,
        shop_id: str,
        buyer_id: str,
        order_id: str,
        amount: float,
        reason: str
    ) -> Dict:
        """自动同意退款"""
        # TODO: 调用平台API同意退款
        
        # 发送通知
        message = f"亲，您的退款申请已审核通过，退款金额¥{amount}将在1-3个工作日内原路退回，请注意查收~"
        
        await self.smart_service.handle_buyer_message(
            shop_id=shop_id,
            buyer_id=buyer_id,
            buyer_message="[系统通知]" + message,
            platform="manual"
        )
        
        logger.info(f"自动同意退款: order_id={order_id}, amount={amount}")
        
        return {
            "success": True,
            "action": "approved",
            "message": message,
            "refund_amount": amount,
            "estimated_time": "1-3个工作日"
        }
    
    async def _transfer_to_manual(
        self,
        shop_id: str,
        buyer_id: str,
        order_id: str,
        after_sales_type: str,
        reason: str
    ) -> Dict:
        """转人工审核"""
        # TODO: 创建售后工单，通知人工客服
        
        type_names = {
            "refund": "退款",
            "return": "退货",
            "exchange": "换货",
            "complaint": "投诉"
        }
        
        logger.info(f"售后申请转人工: order_id={order_id}, type={after_sales_type}")
        
        return {
            "success": True,
            "action": "transferred_to_manual",
            "ticket_id": f"TK{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "message": f"您的{type_names.get(after_sales_type, '售后')}申请已提交，客服将在24小时内处理，请耐心等待~"
        }
    
    async def _generate_after_sales_reply(
        self,
        shop_id: str,
        buyer_id: str,
        after_sales_type: str,
        status: str
    ) -> str:
        """生成售后自动回复"""
        type_names = {
            "refund": "退款",
            "return": "退货",
            "exchange": "换货",
            "complaint": "投诉"
        }
        
        if status == "processing":
            reply = f"亲，您的{type_names.get(after_sales_type, '售后')}申请已收到，我们的售后专员正在审核中，会在24小时内给您答复，请保持手机畅通~ 🙏"
        elif status == "approved":
            reply = f"亲，您的{type_names.get(after_sales_type, '售后')}申请已审核通过，请按照指引操作，如有疑问随时联系我们~ ✅"
        else:
            reply = f"亲，关于您的{type_names.get(after_sales_type, '售后')}申请，我们的客服会尽快与您联系沟通具体事宜，请留意消息~ 📞"
        
        # 发送消息
        await self.smart_service.handle_buyer_message(
            shop_id=shop_id,
            buyer_id=buyer_id,
            buyer_message="[系统通知]" + reply,
            platform="manual"
        )
        
        return reply
    
    async def get_after_sales_list(
        self,
        shop_id: str,
        status: Optional[str] = None,
        type: Optional[str] = None
    ) -> List[Dict]:
        """获取售后申请列表"""
        # TODO: 从数据库查询
        return [
            {
                "id": "AS001",
                "order_id": "ORDER001",
                "buyer_nick": "买家A",
                "type": "refund",
                "reason": "不想要了",
                "amount": 299.00,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "AS002",
                "order_id": "ORDER002",
                "buyer_nick": "买家B",
                "type": "return",
                "reason": "质量问题",
                "amount": 599.00,
                "status": "processing",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
