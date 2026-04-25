"""
订单催付服务 - 自动催付未付款订单
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.services.smart_customer_service import get_smart_customer_service
from app.services.ai.gateway import get_ai_gateway
from app.services.ai_power.billing import BillingService

logger = logging.getLogger(__name__)


class OrderReminderService:
    """订单催付服务"""
    
    # 催付时机（订单创建后的小时数）
    REMINDER_SCHEDULE = [1, 6, 24]  # 1小时、6小时、24小时后催付
    
    # 催付话术模板
    REMINDER_TEMPLATES = {
        1: {
            "subject": "订单待付款提醒",
            "content": "亲，您刚刚下单的商品还在等待付款哦~ 库存有限，建议尽快完成支付，我们会第一时间为您发货！"
        },
        6: {
            "subject": "订单即将关闭提醒",
            "content": "亲，您的订单已经创建6小时了，如果还未付款将在24小时后自动关闭。这款商品很受欢迎，库存不多了，建议您尽快付款锁定库存！"
        },
        24: {
            "subject": "最后催付提醒",
            "content": "亲，这是最后的提醒啦！您的订单将在1小时后自动关闭。如果您还需要这款商品，请立即付款；如果不需要了，订单关闭后欢迎随时回来选购其他商品~"
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.smart_service = get_smart_customer_service(db)
        self.ai_gateway = get_ai_gateway()
        self.billing_service = BillingService()
    
    async def get_pending_orders(
        self,
        shop_id: str,
        hours: int
    ) -> List[Dict]:
        """
        获取待催付的订单
        
        Args:
            shop_id: 商户ID
            hours: 订单创建后的小时数
            
        Returns:
            订单列表
        """
        # 计算时间范围
        now = datetime.utcnow()
        target_time = now - timedelta(hours=hours)
        next_hour = target_time + timedelta(hours=1)
        
        # TODO: 从订单表查询
        # 临时返回模拟数据
        return [
            {
                "order_id": f"ORDER_{i}",
                "buyer_id": f"BUYER_{i}",
                "buyer_nick": f"买家{i}",
                "amount": 299.00,
                "product_name": "示例商品",
                "created_at": target_time.isoformat(),
                "platform": "taobao"
            }
            for i in range(3)
        ]
    
    async def send_reminder(
        self,
        shop_id: str,
        order: Dict,
        hours: int,
        use_ai: bool = True
    ) -> Dict:
        """
        发送催付消息
        
        Args:
            shop_id: 商户ID
            order: 订单信息
            hours: 催付时机（小时）
            use_ai: 是否使用AI生成话术
            
        Returns:
            发送结果
        """
        try:
            buyer_id = order["buyer_id"]
            platform = order["platform"]
            
            if use_ai:
                # 使用AI生成个性化催付话术
                prompt = self._build_reminder_prompt(order, hours)
                
                # 检查余额
                account_info = await self.billing_service.get_account_info(shop_id)
                if account_info['total_available'] <= 0:
                    # 余额不足，使用模板
                    content = self.REMINDER_TEMPLATES[hours]["content"]
                else:
                    # 调用AI生成
                    response = await self.ai_gateway.chat_completion(
                        shop_id=shop_id,
                        model_name="kimi-k2.5",
                        messages=[
                            {"role": "system", "content": "你是一个专业的电商客服，请生成一条友好但有效的催付消息。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    
                    if response.get("success"):
                        content = response["data"]["choices"][0]["message"]["content"]
                    else:
                        content = self.REMINDER_TEMPLATES[hours]["content"]
            else:
                content = self.REMINDER_TEMPLATES[hours]["content"]
            
            # 发送消息
            result = await self.smart_service.handle_buyer_message(
                shop_id=shop_id,
                buyer_id=buyer_id,
                buyer_message="[系统催付]" + content,  # 标记为系统消息
                platform=platform
            )
            
            logger.info(f"催付消息已发送: order_id={order['order_id']}, hours={hours}")
            
            return {
                "success": True,
                "order_id": order["order_id"],
                "buyer_id": buyer_id,
                "content": content,
                "sent_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"催付消息发送失败: {e}", exc_info=True)
            return {
                "success": False,
                "order_id": order.get("order_id"),
                "error": str(e)
            }
    
    def _build_reminder_prompt(self, order: Dict, hours: int) -> str:
        """构建催付提示词"""
        template = self.REMINDER_TEMPLATES[hours]
        
        prompt = f"""请为以下订单生成一条催付消息：

订单信息：
- 商品：{order['product_name']}
- 金额：¥{order['amount']}
- 买家昵称：{order['buyer_nick']}
- 订单创建时间：{order['created_at']}

催付时机：订单创建后{hours}小时
参考话术：{template['content']}

要求：
1. 语气友好亲切，不要过于强硬
2. 可以适当强调商品优势或库存紧张
3. 提醒订单即将关闭（如果是24小时催付）
4. 字数控制在100字以内
5. 使用表情符号增加亲和力

请生成催付消息："""
        
        return prompt
    
    async def run_reminder_task(self, shop_id: str):
        """运行催付任务"""
        for hours in self.REMINDER_SCHEDULE:
            orders = await self.get_pending_orders(shop_id, hours)
            
            for order in orders:
                result = await self.send_reminder(shop_id, order, hours)
                
                if result["success"]:
                    logger.info(f"催付成功: {order['order_id']}")
                else:
                    logger.error(f"催付失败: {order['order_id']}, {result.get('error')}")
        
        return {"success": True, "message": "催付任务执行完成"}
