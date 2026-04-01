"""
系统设置API
管理店铺和系统配置
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List, Dict, Any
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.user import User, Shop
from app.models.system import Setting

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/shop")
async def get_shop_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取店铺设置"""
    if not current_user.shop_id:
        raise HTTPException(status_code=400, detail="用户未绑定店铺")
    
    # 获取店铺信息
    shop = await db.get(Shop, current_user.shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    # 获取店铺设置
    result = await db.execute(
        select(Setting).where(Setting.shop_id == current_user.shop_id)
    )
    settings = result.scalars().all()
    
    # 转换为字典
    settings_dict = {}
    for s in settings:
        if s.value_type == "json":
            import json
            try:
                settings_dict[s.setting_key] = json.loads(s.setting_value)
            except:
                settings_dict[s.setting_key] = s.setting_value
        elif s.value_type == "number":
            try:
                settings_dict[s.setting_key] = float(s.setting_value)
            except:
                settings_dict[s.setting_key] = s.setting_value
        elif s.value_type == "boolean":
            settings_dict[s.setting_key] = s.setting_value.lower() == "true"
        else:
            settings_dict[s.setting_key] = s.setting_value
    
    return {
        "code": 1,
        "data": {
            "shop": {
                "id": str(shop.id),
                "name": shop.name,
                "description": shop.description,
                "status": shop.status,
                "settings": shop.settings or {}
            },
            "settings": settings_dict
        }
    }


@router.put("/shop")
async def update_shop_settings(
    name: Optional[str] = None,
    description: Optional[str] = None,
    settings: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新店铺信息"""
    if not current_user.shop_id:
        raise HTTPException(status_code=400, detail="用户未绑定店铺")
    
    shop = await db.get(Shop, current_user.shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    # 检查权限
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="无权修改店铺信息")
    
    if name:
        shop.name = name
    if description:
        shop.description = description
    if settings:
        shop.settings = settings
    
    await db.commit()
    await db.refresh(shop)
    
    logger.info(f"店铺信息更新: shop_id={shop.id}, user={current_user.username}")
    
    return {
        "code": 1,
        "message": "更新成功",
        "data": {
            "id": str(shop.id),
            "name": shop.name,
            "description": shop.description
        }
    }


@router.get("/ai")
async def get_ai_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取AI设置"""
    shop_id = current_user.shop_id
    
    # 默认设置
    default_settings = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 500,
        "auto_handoff": True,
        "handoff_threshold": 3,
        "max_context_messages": 10,
        "response_timeout": 30
    }
    
    if not shop_id:
        return {
            "code": 1,
            "data": default_settings
        }
    
    # 获取店铺AI设置
    result = await db.execute(
        select(Setting).where(
            and_(
                Setting.shop_id == shop_id,
                Setting.setting_key.like("ai.%")
            )
        )
    )
    settings = result.scalars().all()
    
    # 合并设置
    for s in settings:
        key = s.setting_key.replace("ai.", "")
        if key in default_settings:
            if s.value_type == "number":
                try:
                    default_settings[key] = float(s.setting_value)
                except:
                    pass
            elif s.value_type == "boolean":
                default_settings[key] = s.setting_value.lower() == "true"
            else:
                default_settings[key] = s.setting_value
    
    return {
        "code": 1,
        "data": default_settings
    }


@router.put("/ai")
async def update_ai_settings(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    auto_handoff: Optional[bool] = None,
    handoff_threshold: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新AI设置"""
    if not current_user.shop_id:
        raise HTTPException(status_code=400, detail="用户未绑定店铺")
    
    # 检查权限
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="无权修改AI设置")
    
    settings_to_update = {
        "ai.model": (model, "string"),
        "ai.temperature": (temperature, "number"),
        "ai.max_tokens": (max_tokens, "number"),
        "ai.auto_handoff": (auto_handoff, "boolean"),
        "ai.handoff_threshold": (handoff_threshold, "number")
    }
    
    for key, (value, value_type) in settings_to_update.items():
        if value is None:
            continue
        
        # 查找现有设置
        result = await db.execute(
            select(Setting).where(
                and_(
                    Setting.shop_id == current_user.shop_id,
                    Setting.setting_key == key
                )
            )
        )
        setting = result.scalar_one_or_none()
        
        if setting:
            setting.setting_value = str(value)
            setting.value_type = value_type
        else:
            setting = Setting(
                shop_id=current_user.shop_id,
                setting_key=key,
                setting_value=str(value),
                value_type=value_type
            )
            db.add(setting)
    
    await db.commit()
    
    logger.info(f"AI设置更新: shop_id={current_user.shop_id}, user={current_user.username}")
    
    return {
        "code": 1,
        "message": "更新成功"
    }


@router.get("/conversation")
async def get_conversation_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取对话设置"""
    shop_id = current_user.shop_id
    
    default_settings = {
        "auto_close_hours": 24,
        "max_queue_size": 100,
        "welcome_message": "您好，欢迎咨询！我是AI客服助手，请问有什么可以帮您？",
        "offline_message": "当前为非工作时间，您的留言将在上班后第一时间处理。"
    }
    
    if not shop_id:
        return {
            "code": 1,
            "data": default_settings
        }
    
    result = await db.execute(
        select(Setting).where(
            and_(
                Setting.shop_id == shop_id,
                Setting.setting_key.like("conversation.%")
            )
        )
    )
    settings = result.scalars().all()
    
    for s in settings:
        key = s.setting_key.replace("conversation.", "")
        if key in default_settings:
            if s.value_type == "number":
                try:
                    default_settings[key] = float(s.setting_value)
                except:
                    default_settings[key] = s.setting_value
            else:
                default_settings[key] = s.setting_value
    
    return {
        "code": 1,
        "data": default_settings
    }


@router.put("/conversation")
async def update_conversation_settings(
    auto_close_hours: Optional[int] = None,
    max_queue_size: Optional[int] = None,
    welcome_message: Optional[str] = None,
    offline_message: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新对话设置"""
    if not current_user.shop_id:
        raise HTTPException(status_code=400, detail="用户未绑定店铺")
    
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="无权修改设置")
    
    settings_to_update = {
        "conversation.auto_close_hours": (auto_close_hours, "number"),
        "conversation.max_queue_size": (max_queue_size, "number"),
        "conversation.welcome_message": (welcome_message, "string"),
        "conversation.offline_message": (offline_message, "string")
    }
    
    for key, (value, value_type) in settings_to_update.items():
        if value is None:
            continue
        
        result = await db.execute(
            select(Setting).where(
                and_(
                    Setting.shop_id == current_user.shop_id,
                    Setting.setting_key == key
                )
            )
        )
        setting = result.scalar_one_or_none()
        
        if setting:
            setting.setting_value = str(value)
            setting.value_type = value_type
        else:
            setting = Setting(
                shop_id=current_user.shop_id,
                setting_key=key,
                setting_value=str(value),
                value_type=value_type
            )
            db.add(setting)
    
    await db.commit()
    
    return {
        "code": 1,
        "message": "更新成功"
    }


@router.get("/system")
async def get_system_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取系统设置（仅管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问")
    
    # 获取全局设置
    result = await db.execute(
        select(Setting).where(Setting.shop_id.is_(None))
    )
    settings = result.scalars().all()
    
    settings_dict = {}
    for s in settings:
        settings_dict[s.setting_key] = s.setting_value
    
    return {
        "code": 1,
        "data": settings_dict
    }


@router.put("/system")
async def update_system_settings(
    settings: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新系统设置（仅管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可修改")
    
    for key, value in settings.items():
        result = await db.execute(
            select(Setting).where(
                and_(
                    Setting.shop_id.is_(None),
                    Setting.setting_key == key
                )
            )
        )
        setting = result.scalar_one_or_none()
        
        value_type = "string"
        if isinstance(value, bool):
            value_type = "boolean"
        elif isinstance(value, (int, float)):
            value_type = "number"
        elif isinstance(value, dict):
            import json
            value = json.dumps(value)
            value_type = "json"
        
        if setting:
            setting.setting_value = str(value)
            setting.value_type = value_type
        else:
            setting = Setting(
                shop_id=None,  # 全局设置
                setting_key=key,
                setting_value=str(value),
                value_type=value_type
            )
            db.add(setting)
    
    await db.commit()
    
    logger.info(f"系统设置更新: user={current_user.username}")
    
    return {
        "code": 1,
        "message": "更新成功"
    }
