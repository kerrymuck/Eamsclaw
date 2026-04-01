from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.user import User, Shop, ShopMember
from app.models.stats import DailyStats, HourlyStats, IntentStats

router = APIRouter()


# ============ 数据统计 ============

@router.get("/dashboard")
async def get_dashboard(
    shop_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取仪表盘数据"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == shop.id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该店铺")
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 获取今日统计
    today_result = await db.execute(
        select(DailyStats).where(
            DailyStats.shop_id == uuid.UUID(shop_id),
            DailyStats.stat_date == today
        )
    )
    today_stats = today_result.scalar_one_or_none()
    
    # 获取昨日统计
    yesterday = today - timedelta(days=1)
    yesterday_result = await db.execute(
        select(DailyStats).where(
            DailyStats.shop_id == uuid.UUID(shop_id),
            DailyStats.stat_date == yesterday
        )
    )
    yesterday_stats = yesterday_result.scalar_one_or_none()
    
    # 获取近7天趋势
    week_ago = today - timedelta(days=7)
    week_result = await db.execute(
        select(DailyStats).where(
            DailyStats.shop_id == uuid.UUID(shop_id),
            DailyStats.stat_date >= week_ago
        ).order_by(DailyStats.stat_date)
    )
    week_stats = week_result.scalars().all()
    
    return {
        "today": {
            "total_conversations": today_stats.total_conversations if today_stats else 0,
            "new_conversations": today_stats.new_conversations if today_stats else 0,
            "total_messages": today_stats.total_messages if today_stats else 0,
            "ai_reply_count": today_stats.ai_reply_count if today_stats else 0,
            "handoff_count": today_stats.handoff_count if today_stats else 0,
            "handoff_rate": float(today_stats.handoff_rate) if today_stats else 0,
            "avg_response_time": today_stats.avg_response_time if today_stats else 0,
            "ai_accuracy": float(today_stats.ai_accuracy) if today_stats else 0
        },
        "yesterday": {
            "total_conversations": yesterday_stats.total_conversations if yesterday_stats else 0,
            "new_conversations": yesterday_stats.new_conversations if yesterday_stats else 0,
            "total_messages": yesterday_stats.total_messages if yesterday_stats else 0,
            "handoff_rate": float(yesterday_stats.handoff_rate) if yesterday_stats else 0
        } if yesterday_stats else None,
        "trend": [
            {
                "date": stat.stat_date.strftime("%Y-%m-%d"),
                "conversations": stat.total_conversations,
                "messages": stat.total_messages,
                "handoff_rate": float(stat.handoff_rate)
            }
            for stat in week_stats
        ]
    }


@router.get("/daily")
async def get_daily_stats(
    shop_id: str,
    start_date: str,
    end_date: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取每日统计"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == shop.id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该店铺")
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    result = await db.execute(
        select(DailyStats).where(
            DailyStats.shop_id == uuid.UUID(shop_id),
            DailyStats.stat_date >= start,
            DailyStats.stat_date <= end
        ).order_by(DailyStats.stat_date)
    )
    stats = result.scalars().all()
    
    return {
        "stats": [
            {
                "date": stat.stat_date.strftime("%Y-%m-%d"),
                "total_conversations": stat.total_conversations,
                "new_conversations": stat.new_conversations,
                "closed_conversations": stat.closed_conversations,
                "total_messages": stat.total_messages,
                "user_messages": stat.user_messages,
                "ai_messages": stat.ai_messages,
                "manual_messages": stat.manual_messages,
                "avg_response_time": stat.avg_response_time,
                "handoff_count": stat.handoff_count,
                "handoff_rate": float(stat.handoff_rate),
                "ai_reply_count": stat.ai_reply_count,
                "ai_accuracy": float(stat.ai_accuracy)
            }
            for stat in stats
        ]
    }


@router.get("/hourly")
async def get_hourly_stats(
    shop_id: str,
    date: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取小时统计"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == shop.id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该店铺")
    
    stat_date = datetime.strptime(date, "%Y-%m-%d")
    
    result = await db.execute(
        select(HourlyStats).where(
            HourlyStats.shop_id == uuid.UUID(shop_id),
            HourlyStats.stat_date == stat_date
        ).order_by(HourlyStats.stat_hour)
    )
    stats = result.scalars().all()
    
    return {
        "date": date,
        "stats": [
            {
                "hour": stat.stat_hour,
                "conversation_count": stat.conversation_count,
                "message_count": stat.message_count,
                "avg_response_time": stat.avg_response_time,
                "handoff_count": stat.handoff_count
            }
            for stat in stats
        ]
    }


@router.get("/intents")
async def get_intent_stats(
    shop_id: str,
    start_date: str,
    end_date: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取意图统计"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == shop.id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该店铺")
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    result = await db.execute(
        select(
            IntentStats.intent,
            func.sum(IntentStats.count).label('total_count'),
            func.avg(IntentStats.avg_confidence).label('avg_confidence')
        ).where(
            IntentStats.shop_id == uuid.UUID(shop_id),
            IntentStats.stat_date >= start,
            IntentStats.stat_date <= end
        ).group_by(IntentStats.intent)
        .order_by(desc('total_count'))
    )
    stats = result.all()
    
    return {
        "intents": [
            {
                "intent": stat.intent,
                "count": int(stat.total_count),
                "avg_confidence": float(stat.avg_confidence) if stat.avg_confidence else 0
            }
            for stat in stats
        ]
    }


@router.get("/agents")
async def get_agent_stats(
    shop_id: str,
    date: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取客服统计"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == shop.id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该店铺")
    
    # TODO: 实现客服统计查询
    # 这里返回模拟数据
    return {
        "date": date,
        "agents": [
            {
                "user_id": "agent-1",
                "username": "客服小王",
                "conversations_handled": 25,
                "messages_sent": 150,
                "avg_response_time": 120,
                "satisfaction_rate": 0.95
            },
            {
                "user_id": "agent-2",
                "username": "客服小李",
                "conversations_handled": 30,
                "messages_sent": 180,
                "avg_response_time": 90,
                "satisfaction_rate": 0.92
            }
        ]
    }


# ============ 实时统计 ============

@router.get("/realtime")
async def get_realtime_stats(
    shop_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取实时统计数据"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == shop.id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该店铺")
    
    # TODO: 从Redis获取实时数据
    # 这里返回模拟数据
    return {
        "online_agents": 5,
        "active_conversations": 12,
        "pending_handoffs": 3,
        "avg_wait_time": 45,
        "messages_per_minute": 8
    }
