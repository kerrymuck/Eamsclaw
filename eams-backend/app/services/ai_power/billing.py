"""
AI计费服务 - 余额管理、扣费、交易记录
"""

import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Tuple
from sqlalchemy.orm import Session
import uuid

from app.models.ai_power import (
    AIAccount, AITransaction, AIUsage, AIModelPrice, RechargeOrder
)
from app.models.user import Shop
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class BillingService:
    """AI计费服务"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    async def get_or_create_account(self, shop_id: str) -> AIAccount:
        """获取或创建AI账户"""
        # 将字符串转换为UUID
        if isinstance(shop_id, str):
            shop_id_uuid = uuid.UUID(shop_id)
        else:
            shop_id_uuid = shop_id
            
        account = self.db.query(AIAccount).filter(
            AIAccount.shop_id == shop_id_uuid
        ).first()
        
        if not account:
            # 检查商户是否存在
            shop = self.db.query(Shop).filter(Shop.id == shop_id_uuid).first()
            if not shop:
                raise ValueError(f"商户不存在: {shop_id}")
            
            # 创建新账户
            account = AIAccount(
                shop_id=shop_id_uuid,
                balance=Decimal("0"),
                free_quota=Decimal("20"),  # 新用户赠送20元
                status='active'
            )
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)
            
            logger.info(f"创建AI账户: shop_id={shop_id}")
        
        return account
    
    async def check_balance(
        self,
        shop_id: str,
        estimated_cost: Dict[str, Decimal]
    ) -> Tuple[bool, Dict]:
        """
        检查余额是否充足
        
        Returns:
            (是否充足, 余额信息)
        """
        account = await self.get_or_create_account(shop_id)
        
        available = account.balance + account.free_quota
        required = estimated_cost["total_cost"]
        
        return available >= required, {
            "balance": float(account.balance),
            "free_quota": float(account.free_quota),
            "available": float(available),
            "required": float(required)
        }
    
    async def deduct_balance(
        self,
        shop_id: str,
        amount: Dict[str, Decimal],
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        conversation_id: Optional[str] = None,
        message_id: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        provider_id: Optional[str] = None
    ) -> bool:
        """
        扣除余额并记录用量
        
        Args:
            shop_id: 商户ID
            amount: 费用信息 {input_cost, output_cost, total_cost}
            model_name: 模型名称
            input_tokens: 输入token数
            output_tokens: 输出token数
            conversation_id: 对话ID
            message_id: 消息ID
            response_time_ms: 响应时间
            provider_id: 服务商ID
            
        Returns:
            是否成功
        """
        try:
            account = await self.get_or_create_account(shop_id)
            total_cost = amount["total_cost"]
            
            # 1. 优先使用免费额度
            free_quota_used = Decimal("0")
            balance_used = Decimal("0")
            
            if account.free_quota > 0:
                free_quota_used = min(account.free_quota, total_cost)
                account.free_quota -= free_quota_used
            
            remaining = total_cost - free_quota_used
            if remaining > 0:
                if account.balance < remaining:
                    logger.error(f"余额不足: shop_id={shop_id}, balance={account.balance}, required={remaining}")
                    self.db.rollback()
                    return False
                
                balance_used = remaining
                account.balance -= remaining
            
            account.total_consumed += total_cost
            account.updated_at = datetime.utcnow()
            
            # 2. 记录用量
            usage = AIUsage(
                shop_id=shop_id,
                provider_id=provider_id,
                model_name=model_name,
                model_provider=self._get_model_provider(model_name),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                input_cost=amount["input_cost"],
                output_cost=amount["output_cost"],
                total_cost=total_cost,
                conversation_id=conversation_id,
                message_id=message_id,
                response_time_ms=response_time_ms,
                status='success'
            )
            self.db.add(usage)
            
            # 3. 记录交易
            transaction = AITransaction(
                shop_id=shop_id,
                type='consumption',
                amount=-total_cost,  # 消费为负
                balance_after=account.balance + account.free_quota,
                description=f"AI调用: {model_name}, 输入{input_tokens}tokens, 输出{output_tokens}tokens",
                reference_id=usage.id,
                reference_type='usage'
            )
            self.db.add(transaction)
            
            self.db.commit()
            
            logger.info(
                f"扣费成功: shop_id={shop_id}, model={model_name}, "
                f"cost={total_cost}, free_used={free_quota_used}, balance_used={balance_used}"
            )
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"扣费失败: {e}", exc_info=True)
            return False
    
    async def recharge(
        self,
        shop_id: str,
        amount: Decimal,
        order_id: str,
        payment_method: str
    ) -> bool:
        """
        充值
        
        Args:
            shop_id: 商户ID
            amount: 充值金额
            order_id: 订单ID
            payment_method: 支付方式
            
        Returns:
            是否成功
        """
        try:
            account = await self.get_or_create_account(shop_id)
            
            old_balance = account.balance
            account.balance += amount
            account.total_recharged += amount
            account.updated_at = datetime.utcnow()
            
            # 记录交易
            transaction = AITransaction(
                shop_id=shop_id,
                type='recharge',
                amount=amount,
                balance_after=account.balance + account.free_quota,
                description=f"充值: {payment_method}",
                reference_id=order_id,
                reference_type='order'
            )
            self.db.add(transaction)
            
            self.db.commit()
            
            logger.info(
                f"充值成功: shop_id={shop_id}, amount={amount}, "
                f"balance={old_balance} -> {account.balance}"
            )
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"充值失败: {e}", exc_info=True)
            return False
    
    async def get_account_info(self, shop_id: str) -> Dict:
        """获取账户信息"""
        account = await self.get_or_create_account(shop_id)
        
        return {
            "balance": float(account.balance),
            "free_quota": float(account.free_quota),
            "total_available": float(account.balance + account.free_quota),
            "total_recharged": float(account.total_recharged),
            "total_consumed": float(account.total_consumed),
            "status": account.status
        }
    
    async def get_model_price(self, model_name: str) -> Optional[AIModelPrice]:
        """获取模型价格配置"""
        return self.db.query(AIModelPrice).filter(
            AIModelPrice.model_name == model_name,
            AIModelPrice.is_active == True
        ).first()
    
    async def get_available_models(self) -> list:
        """获取可用模型列表"""
        models = self.db.query(AIModelPrice).filter(
            AIModelPrice.is_active == True
        ).order_by(AIModelPrice.sort_order).all()
        
        # 模型性能指标映射
        model_metrics = {
            'GPT-4': {'response_time': 1200, 'accuracy': 96, 'cost_performance': '中', 'star_rating': 4.8},
            'GPT-4o': {'response_time': 600, 'accuracy': 94, 'cost_performance': '高', 'star_rating': 4.7},
            'Claude 3.5': {'response_time': 900, 'accuracy': 93, 'cost_performance': '中', 'star_rating': 4.6},
            'Kimi K2.5': {'response_time': 850, 'accuracy': 92, 'cost_performance': '高', 'star_rating': 4.5},
            '文心一言4.0': {'response_time': 700, 'accuracy': 88, 'cost_performance': '中', 'star_rating': 4.2},
            '通义千问Max': {'response_time': 750, 'accuracy': 89, 'cost_performance': '高', 'star_rating': 4.3},
            '豆包Pro': {'response_time': 500, 'accuracy': 85, 'cost_performance': '极高', 'star_rating': 4.4},
            'GLM-4': {'response_time': 800, 'accuracy': 87, 'cost_performance': '高', 'star_rating': 4.1},
        }
        
        return [
            {
                "id": m.model_name,
                "name": m.model_name,
                "provider": m.provider,
                "input_price": float(m.official_input_price),
                "output_price": float(m.official_output_price),
                "features": m.features or [],
                "icon": m.icon,
                "context_length": m.context_length,
                "max_tokens": m.max_tokens,
                "is_recommended": m.is_recommended,
                **model_metrics.get(m.model_name, {'response_time': 800, 'accuracy': 90, 'cost_performance': '中', 'star_rating': 4.0})
            }
            for m in models
        ]
    
    async def get_usage_stats(
        self,
        shop_id: str,
        days: int = 30
    ) -> Dict:
        """获取用量统计"""
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 总用量
        total_usage = self.db.query(AIUsage).filter(
            AIUsage.shop_id == shop_id,
            AIUsage.created_at >= start_date
        )
        
        total_tokens = sum(u.total_tokens for u in total_usage.all())
        total_cost = sum(float(u.total_cost) for u in total_usage.all())
        total_calls = total_usage.count()
        
        # 按模型分组
        model_stats = {}
        for usage in total_usage.all():
            model = usage.model_name
            if model not in model_stats:
                model_stats[model] = {
                    "tokens": 0,
                    "cost": 0,
                    "calls": 0
                }
            model_stats[model]["tokens"] += usage.total_tokens
            model_stats[model]["cost"] += float(usage.total_cost)
            model_stats[model]["calls"] += 1
        
        return {
            "period_days": days,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "total_calls": total_calls,
            "avg_cost_per_call": total_cost / total_calls if total_calls > 0 else 0,
            "model_breakdown": model_stats
        }
    
    def _get_model_provider(self, model_name: str) -> str:
        """根据模型名称获取提供商"""
        provider_map = {
            "gpt-4": "openai",
            "gpt-4o": "openai",
            "gpt-3.5": "openai",
            "claude": "anthropic",
            "kimi": "moonshot",
            "wenxin": "baidu",
            "qwen": "alibaba",
            "glm": "zhipu",
            "doubao": "bytedance"
        }
        
        for key, provider in provider_map.items():
            if key in model_name.lower():
                return provider
        
        return "unknown"
