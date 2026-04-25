"""
结算分润服务 - 平台与服务商分润结算
"""

import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ai_power import (
    AIUsage, AIAccount, AITransaction, ProviderSettlement, AIModelPrice
)
from app.models.user import User, Shop
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class SettlementService:
    """结算分润服务"""
    
    # 服务商等级折扣
    PROVIDER_DISCOUNTS = {
        'normal': Decimal('1.0'),    # 普通服务商：100%
        'bronze': Decimal('0.85'),   # 铜牌：85%
        'silver': Decimal('0.75'),   # 银牌：75%
        'gold': Decimal('0.60'),     # 金牌：60%
    }
    
    def __init__(self):
        self.db = SessionLocal()
    
    async def calculate_provider_settlement(
        self,
        provider_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        计算服务商结算
        
        Args:
            provider_id: 服务商ID
            start_date: 结算周期开始
            end_date: 结算周期结束
            
        Returns:
            {
                "provider_id": "...",
                "period": {"start": "...", "end": "..."},
                "total_usage": 总用量金额,
                "platform_cost": 平台成本,
                "provider_profit": 服务商分润,
                "platform_profit": 平台利润,
                "details": [...]
            }
        """
        # 1. 获取服务商信息
        provider = self.db.query(User).filter(
            User.id == provider_id,
            User.role == 'provider'
        ).first()
        
        if not provider:
            raise ValueError(f"服务商不存在: {provider_id}")
        
        # 2. 获取服务商等级
        provider_level = getattr(provider, 'provider_level', 'normal')
        discount = self.PROVIDER_DISCOUNTS.get(provider_level, Decimal('1.0'))
        
        # 3. 查询该服务商旗下所有商户的用量
        # 假设商户表中有 provider_id 字段关联服务商
        shops = self.db.query(Shop).filter(
            Shop.provider_id == provider_id
        ).all()
        
        shop_ids = [str(shop.id) for shop in shops]
        
        # 4. 统计用量
        usage_stats = self.db.query(
            AIUsage.model_name,
            func.sum(AIUsage.input_tokens).label('total_input_tokens'),
            func.sum(AIUsage.output_tokens).label('total_output_tokens'),
            func.sum(AIUsage.total_cost).label('total_cost')
        ).filter(
            AIUsage.shop_id.in_(shop_ids),
            AIUsage.created_at >= start_date,
            AIUsage.created_at <= end_date
        ).group_by(AIUsage.model_name).all()
        
        # 5. 计算分润
        total_usage = Decimal('0')
        platform_cost = Decimal('0')
        details = []
        
        for stat in usage_stats:
            model_name = stat.model_name
            model_cost = Decimal(str(stat.total_cost))
            
            # 获取模型价格配置
            model_price = self.db.query(AIModelPrice).filter(
                AIModelPrice.model_name == model_name
            ).first()
            
            if model_price:
                # 平台成本 = 官方零售价 × 折扣
                input_cost = (Decimal(str(stat.total_input_tokens)) / 1000) * \
                           Decimal(str(model_price.official_input_price)) * discount
                output_cost = (Decimal(str(stat.total_output_tokens)) / 1000) * \
                            Decimal(str(model_price.official_output_price)) * discount
                cost = input_cost + output_cost
            else:
                # 默认按70%计算成本
                cost = model_cost * Decimal('0.7')
            
            profit = model_cost - cost
            
            total_usage += model_cost
            platform_cost += cost
            
            details.append({
                "model_name": model_name,
                "input_tokens": int(stat.total_input_tokens),
                "output_tokens": int(stat.total_output_tokens),
                "total_cost": float(model_cost),
                "platform_cost": float(cost),
                "profit": float(profit)
            })
        
        provider_profit = total_usage - platform_cost
        platform_profit = provider_profit  # 平台利润 = 服务商分润（对称设计）
        
        return {
            "provider_id": provider_id,
            "provider_name": provider.username,
            "provider_level": provider_level,
            "discount": float(discount),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_usage": float(total_usage),
            "platform_cost": float(platform_cost),
            "provider_profit": float(provider_profit),
            "platform_profit": float(platform_profit),
            "shop_count": len(shops),
            "details": details
        }
    
    async def create_settlement(
        self,
        provider_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> ProviderSettlement:
        """创建结算单"""
        # 计算结算数据
        settlement_data = await self.calculate_provider_settlement(
            provider_id, start_date, end_date
        )
        
        # 创建结算记录
        settlement = ProviderSettlement(
            provider_id=provider_id,
            period_start=start_date,
            period_end=end_date,
            total_usage=Decimal(str(settlement_data['total_usage'])),
            platform_cost=Decimal(str(settlement_data['platform_cost'])),
            provider_profit=Decimal(str(settlement_data['provider_profit'])),
            platform_profit=Decimal(str(settlement_data['platform_profit'])),
            status='pending'
        )
        
        self.db.add(settlement)
        self.db.commit()
        self.db.refresh(settlement)
        
        logger.info(
            f"创建结算单: provider_id={provider_id}, "
            f"amount={settlement_data['provider_profit']}, "
            f"period={start_date.date()} to {end_date.date()}"
        )
        
        return settlement
    
    async def settle_provider(
        self,
        settlement_id: str
    ) -> bool:
        """
        执行结算
        
        将分润金额打入服务商账户
        """
        settlement = self.db.query(ProviderSettlement).filter(
            ProviderSettlement.id == settlement_id
        ).first()
        
        if not settlement:
            raise ValueError(f"结算单不存在: {settlement_id}")
        
        if settlement.status != 'pending':
            raise ValueError(f"结算单状态错误: {settlement.status}")
        
        try:
            # TODO: 实际打款逻辑（对接支付系统）
            # 1. 转账到服务商账户
            # 2. 记录转账流水
            
            settlement.status = 'settled'
            settlement.settled_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"结算完成: settlement_id={settlement_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"结算失败: {e}", exc_info=True)
            return False
    
    async def get_provider_settlements(
        self,
        provider_id: str,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """获取服务商结算列表"""
        query = self.db.query(ProviderSettlement).filter(
            ProviderSettlement.provider_id == provider_id
        )
        
        if status:
            query = query.filter(ProviderSettlement.status == status)
        
        total = query.count()
        items = query.order_by(
            ProviderSettlement.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [
                {
                    "id": str(item.id),
                    "period_start": item.period_start.isoformat(),
                    "period_end": item.period_end.isoformat(),
                    "total_usage": float(item.total_usage),
                    "provider_profit": float(item.provider_profit),
                    "status": item.status,
                    "settled_at": item.settled_at.isoformat() if item.settled_at else None,
                    "created_at": item.created_at.isoformat()
                }
                for item in items
            ]
        }
    
    async def get_platform_revenue(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        获取平台收入统计
        
        用于超管后台查看整体营收
        """
        # 总消费金额（商户支付）
        total_consumption = self.db.query(
            func.sum(AIUsage.total_cost)
        ).filter(
            AIUsage.created_at >= start_date,
            AIUsage.created_at <= end_date
        ).scalar() or Decimal('0')
        
        # 平台成本（按零售价×折扣计算）
        # 简化计算：假设平均折扣为75%
        avg_discount = Decimal('0.75')
        platform_cost = total_consumption * avg_discount
        
        # 平台毛利
        platform_profit = total_consumption - platform_cost
        
        # 按模型统计
        model_stats = self.db.query(
            AIUsage.model_name,
            func.sum(AIUsage.total_cost).label('revenue'),
            func.sum(AIUsage.total_tokens).label('tokens')
        ).filter(
            AIUsage.created_at >= start_date,
            AIUsage.created_at <= end_date
        ).group_by(AIUsage.model_name).all()
        
        # 按天统计
        daily_stats = self.db.query(
            func.date(AIUsage.created_at).label('date'),
            func.sum(AIUsage.total_cost).label('revenue')
        ).filter(
            AIUsage.created_at >= start_date,
            AIUsage.created_at <= end_date
        ).group_by(func.date(AIUsage.created_at)).all()
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_revenue": float(total_consumption),
            "platform_cost": float(platform_cost),
            "platform_profit": float(platform_profit),
            "profit_margin": float(platform_profit / total_consumption * 100) if total_consumption > 0 else 0,
            "model_breakdown": [
                {
                    "model": stat.model_name,
                    "revenue": float(stat.revenue),
                    "tokens": int(stat.tokens)
                }
                for stat in model_stats
            ],
            "daily_trend": [
                {
                    "date": str(stat.date),
                    "revenue": float(stat.revenue)
                }
                for stat in daily_stats
            ]
        }
    
    async def auto_settle_monthly(self):
        """
        自动月结
        
        每月1号自动结算上个月的账单
        """
        today = datetime.utcnow()
        # 上个月
        if today.month == 1:
            last_month = today.replace(year=today.year - 1, month=12, day=1)
        else:
            last_month = today.replace(month=today.month - 1, day=1)
        
        # 计算起止时间
        start_date = last_month.replace(day=1, hour=0, minute=0, second=0)
        if last_month.month == 12:
            end_date = last_month.replace(year=last_month.year + 1, month=1, day=1)
        else:
            end_date = last_month.replace(month=last_month.month + 1, day=1)
        end_date = end_date - timedelta(seconds=1)
        
        # 获取所有服务商
        providers = self.db.query(User).filter(
            User.role == 'provider'
        ).all()
        
        settlements = []
        for provider in providers:
            try:
                settlement = await self.create_settlement(
                    str(provider.id),
                    start_date,
                    end_date
                )
                settlements.append(settlement)
            except Exception as e:
                logger.error(f"自动结算失败: provider_id={provider.id}, error={e}")
        
        logger.info(f"自动月结完成: 共{len(settlements)}个结算单")
        return settlements
