"""
定时任务模块
使用 APScheduler 实现定时任务
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import logging

from app.core.database import AsyncSessionLocal
from app.models.stats import DailyStats, HourlyStats, IntentStats
from app.models.conversation import Conversation, Message
from sqlalchemy import select, func, and_

logger = logging.getLogger(__name__)

# 全局调度器
scheduler = AsyncIOScheduler()


async def calculate_hourly_stats():
    """计算小时统计"""
    async with AsyncSessionLocal() as db:
        try:
            now = datetime.utcnow()
            stat_date = now.date()
            stat_hour = now.hour
            
            # 获取前一小时的数据
            hour_start = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
            hour_end = hour_start + timedelta(hours=1)
            
            # 查询所有店铺
            from app.models.user import Shop
            result = await db.execute(select(Shop))
            shops = result.scalars().all()
            
            for shop in shops:
                # 统计对话数
                conv_result = await db.execute(
                    select(func.count(Conversation.id)).where(
                        and_(
                            Conversation.shop_id == shop.id,
                            Conversation.created_at >= hour_start,
                            Conversation.created_at < hour_end
                        )
                    )
                )
                conversation_count = conv_result.scalar() or 0
                
                # 统计消息数
                msg_result = await db.execute(
                    select(func.count(Message.id)).where(
                        and_(
                            Message.conversation_id.in_(
                                select(Conversation.id).where(Conversation.shop_id == shop.id)
                            ),
                            Message.created_at >= hour_start,
                            Message.created_at < hour_end
                        )
                    )
                )
                message_count = msg_result.scalar() or 0
                
                # 计算平均响应时间
                response_result = await db.execute(
                    select(func.avg(Message.response_time)).where(
                        and_(
                            Message.conversation_id.in_(
                                select(Conversation.id).where(Conversation.shop_id == shop.id)
                            ),
                            Message.created_at >= hour_start,
                            Message.created_at < hour_end,
                            Message.response_time.isnot(None)
                        )
                    )
                )
                avg_response_time = int(response_result.scalar() or 0)
                
                # 统计转人工数
                handoff_result = await db.execute(
                    select(func.count(Conversation.id)).where(
                        and_(
                            Conversation.shop_id == shop.id,
                            Conversation.handoff_at >= hour_start,
                            Conversation.handoff_at < hour_end
                        )
                    )
                )
                handoff_count = handoff_result.scalar() or 0
                
                # 保存或更新小时统计
                result = await db.execute(
                    select(HourlyStats).where(
                        and_(
                            HourlyStats.shop_id == shop.id,
                            HourlyStats.stat_date == stat_date,
                            HourlyStats.stat_hour == stat_hour
                        )
                    )
                )
                hourly_stat = result.scalar_one_or_none()
                
                if hourly_stat:
                    hourly_stat.conversation_count = conversation_count
                    hourly_stat.message_count = message_count
                    hourly_stat.avg_response_time = avg_response_time
                    hourly_stat.handoff_count = handoff_count
                else:
                    hourly_stat = HourlyStats(
                        shop_id=shop.id,
                        stat_date=stat_date,
                        stat_hour=stat_hour,
                        conversation_count=conversation_count,
                        message_count=message_count,
                        avg_response_time=avg_response_time,
                        handoff_count=handoff_count
                    )
                    db.add(hourly_stat)
            
            await db.commit()
            logger.info(f"小时统计计算完成: {stat_date} {stat_hour}:00")
        
        except Exception as e:
            logger.error(f"计算小时统计失败: {e}")
            await db.rollback()


async def calculate_daily_stats():
    """计算每日统计"""
    async with AsyncSessionLocal() as db:
        try:
            yesterday = (datetime.utcnow() - timedelta(days=1)).date()
            
            # 查询所有店铺
            from app.models.user import Shop
            result = await db.execute(select(Shop))
            shops = result.scalars().all()
            
            for shop in shops:
                day_start = datetime.combine(yesterday, datetime.min.time())
                day_end = day_start + timedelta(days=1)
                
                # 总会话数
                total_conv_result = await db.execute(
                    select(func.count(Conversation.id)).where(
                        and_(
                            Conversation.shop_id == shop.id,
                            Conversation.created_at >= day_start,
                            Conversation.created_at < day_end
                        )
                    )
                )
                total_conversations = total_conv_result.scalar() or 0
                
                # 已关闭会话数
                closed_conv_result = await db.execute(
                    select(func.count(Conversation.id)).where(
                        and_(
                            Conversation.shop_id == shop.id,
                            Conversation.status == "closed",
                            Conversation.closed_at >= day_start,
                            Conversation.closed_at < day_end
                        )
                    )
                )
                closed_conversations = closed_conv_result.scalar() or 0
                
                # 活跃会话数
                active_conversations = total_conversations - closed_conversations
                
                # 总消息数
                total_msg_result = await db.execute(
                    select(func.count(Message.id)).where(
                        and_(
                            Message.conversation_id.in_(
                                select(Conversation.id).where(Conversation.shop_id == shop.id)
                            ),
                            Message.created_at >= day_start,
                            Message.created_at < day_end
                        )
                    )
                )
                total_messages = total_msg_result.scalar() or 0
                
                # AI消息数
                ai_msg_result = await db.execute(
                    select(func.count(Message.id)).where(
                        and_(
                            Message.conversation_id.in_(
                                select(Conversation.id).where(Conversation.shop_id == shop.id)
                            ),
                            Message.sender_type == "ai",
                            Message.created_at >= day_start,
                            Message.created_at < day_end
                        )
                    )
                )
                ai_messages = ai_msg_result.scalar() or 0
                
                # 人工消息数
                manual_messages = total_messages - ai_msg_result.scalar() or 0
                
                # 转人工数
                handoff_result = await db.execute(
                    select(func.count(Conversation.id)).where(
                        and_(
                            Conversation.shop_id == shop.id,
                            Conversation.handoff_at >= day_start,
                            Conversation.handoff_at < day_end
                        )
                    )
                )
                handoff_count = handoff_result.scalar() or 0
                
                # 转人工率
                handoff_rate = (handoff_count / total_conversations * 100) if total_conversations > 0 else 0
                
                # 保存或更新日统计
                result = await db.execute(
                    select(DailyStats).where(
                        and_(
                            DailyStats.shop_id == shop.id,
                            DailyStats.stat_date == yesterday
                        )
                    )
                )
                daily_stat = result.scalar_one_or_none()
                
                if daily_stat:
                    daily_stat.total_conversations = total_conversations
                    daily_stat.closed_conversations = closed_conversations
                    daily_stat.active_conversations = active_conversations
                    daily_stat.total_messages = total_messages
                    daily_stat.ai_messages = ai_messages
                    daily_stat.manual_messages = manual_messages
                    daily_stat.handoff_count = handoff_count
                    daily_stat.handoff_rate = handoff_rate
                else:
                    daily_stat = DailyStats(
                        shop_id=shop.id,
                        stat_date=yesterday,
                        total_conversations=total_conversations,
                        closed_conversations=closed_conversations,
                        active_conversations=active_conversations,
                        total_messages=total_messages,
                        ai_messages=ai_messages,
                        manual_messages=manual_messages,
                        handoff_count=handoff_count,
                        handoff_rate=handoff_rate
                    )
                    db.add(daily_stat)
            
            await db.commit()
            logger.info(f"日统计计算完成: {yesterday}")
        
        except Exception as e:
            logger.error(f"计算日统计失败: {e}")
            await db.rollback()


async def calculate_intent_stats():
    """计算意图统计"""
    async with AsyncSessionLocal() as db:
        try:
            yesterday = (datetime.utcnow() - timedelta(days=1)).date()
            day_start = datetime.combine(yesterday, datetime.min.time())
            day_end = day_start + timedelta(days=1)
            
            # 查询所有店铺
            from app.models.user import Shop
            result = await db.execute(select(Shop))
            shops = result.scalars().all()
            
            for shop in shops:
                # 按意图分组统计
                intent_result = await db.execute(
                    select(
                        Message.intent,
                        func.count(Message.id).label("count"),
                        func.avg(Message.intent_confidence).label("avg_confidence")
                    ).where(
                        and_(
                            Message.conversation_id.in_(
                                select(Conversation.id).where(Conversation.shop_id == shop.id)
                            ),
                            Message.intent.isnot(None),
                            Message.created_at >= day_start,
                            Message.created_at < day_end
                        )
                    ).group_by(Message.intent)
                )
                
                for row in intent_result:
                    intent, count, avg_confidence = row
                    
                    # 保存或更新意图统计
                    result = await db.execute(
                        select(IntentStats).where(
                            and_(
                                IntentStats.shop_id == shop.id,
                                IntentStats.stat_date == yesterday,
                                IntentStats.intent == intent
                            )
                        )
                    )
                    intent_stat = result.scalar_one_or_none()
                    
                    if intent_stat:
                        intent_stat.count = count
                        intent_stat.avg_confidence = float(avg_confidence or 0)
                    else:
                        intent_stat = IntentStats(
                            shop_id=shop.id,
                            stat_date=yesterday,
                            intent=intent,
                            count=count,
                            avg_confidence=float(avg_confidence or 0)
                        )
                        db.add(intent_stat)
            
            await db.commit()
            logger.info(f"意图统计计算完成: {yesterday}")
        
        except Exception as e:
            logger.error(f"计算意图统计失败: {e}")
            await db.rollback()


async def auto_close_conversations():
    """自动关闭长时间未活跃的会话"""
    async with AsyncSessionLocal() as db:
        try:
            # 24小时无消息的会话自动关闭
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            result = await db.execute(
                select(Conversation).where(
                    and_(
                        Conversation.status == "active",
                        Conversation.last_message_at < cutoff_time
                    )
                )
            )
            
            conversations = result.scalars().all()
            
            for conv in conversations:
                conv.status = "closed"
                conv.closed_at = datetime.utcnow()
                conv.close_reason = "auto_timeout"
            
            await db.commit()
            logger.info(f"自动关闭 {len(conversations)} 个超时会话")
        
        except Exception as e:
            logger.error(f"自动关闭会话失败: {e}")
            await db.rollback()


def init_scheduler():
    """初始化调度器"""
    # 每小时统计
    scheduler.add_job(
        calculate_hourly_stats,
        trigger=CronTrigger(minute=5),  # 每小时的第5分钟执行
        id="hourly_stats",
        replace_existing=True
    )
    
    # 每日统计 (每天凌晨1点)
    scheduler.add_job(
        calculate_daily_stats,
        trigger=CronTrigger(hour=1, minute=0),
        id="daily_stats",
        replace_existing=True
    )
    
    # 意图统计 (每天凌晨2点)
    scheduler.add_job(
        calculate_intent_stats,
        trigger=CronTrigger(hour=2, minute=0),
        id="intent_stats",
        replace_existing=True
    )
    
    # 自动关闭会话 (每小时执行)
    scheduler.add_job(
        auto_close_conversations,
        trigger=IntervalTrigger(hours=1),
        id="auto_close",
        replace_existing=True
    )
    
    logger.info("定时任务调度器初始化完成")


def start_scheduler():
    """启动调度器"""
    if not scheduler.running:
        scheduler.start()
        logger.info("定时任务调度器已启动")


def shutdown_scheduler():
    """关闭调度器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("定时任务调度器已关闭")
