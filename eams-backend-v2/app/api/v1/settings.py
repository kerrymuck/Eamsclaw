from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.base import success_response
from app.middlewares.auth import require_super_admin
from app.services.setting import setting_service
from app.models.setting import SettingGroup

router = APIRouter()


class SettingCreate(BaseModel):
    key: str
    value: str
    group: str = "general"
    description: Optional[str] = None


class SettingUpdate(BaseModel):
    value: str


class BatchSettingUpdate(BaseModel):
    settings: List[dict]


@router.get("")
async def list_settings(
    group: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """获取设置列表"""
    if group:
        try:
            group_enum = SettingGroup(group)
            settings = await setting_service.get_by_group(db, group_enum)
        except ValueError:
            settings = []
    else:
        settings = await setting_service.get_all(db, limit=1000)
    
    return success_response({
        s.key: {
            "value": s.value,
            "group": s.group.value,
            "description": s.description
        }
        for s in settings
    })


@router.get("/{key}")
async def get_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """获取单个设置"""
    setting = await setting_service.get_by_key(db, key)
    if not setting:
        from app.exceptions import NotFoundError
        raise NotFoundError("设置不存在")
    
    return success_response({
        "key": setting.key,
        "value": setting.value,
        "group": setting.group.value,
        "description": setting.description
    })


@router.post("")
async def create_setting(
    data: SettingCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """创建设置"""
    try:
        group_enum = SettingGroup(data.group)
    except ValueError:
        group_enum = SettingGroup.GENERAL
    
    setting = await setting_service.set_value(
        db,
        key=data.key,
        value=data.value,
        group=group_enum,
        description=data.description
    )
    return success_response({"key": setting.key}, message="创建成功")


@router.put("/{key}")
async def update_setting(
    key: str,
    data: SettingUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """更新设置"""
    setting = await setting_service.set_value(db, key, data.value)
    if not setting:
        from app.exceptions import NotFoundError
        raise NotFoundError("设置不存在")
    return success_response({"key": setting.key}, message="更新成功")


@router.post("/batch")
async def batch_update_settings(
    data: BatchSettingUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """批量更新设置"""
    settings_dict = {item["key"]: item["value"] for item in data.settings if "key" in item and "value" in item}
    await setting_service.batch_update(db, settings_dict)
    return success_response(message="批量更新成功")


@router.delete("/{key}")
async def delete_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """删除设置"""
    setting = await setting_service.get_by_key(db, key)
    if not setting:
        from app.exceptions import NotFoundError
        raise NotFoundError("设置不存在")
    
    await setting_service.delete(db, setting.id)
    return success_response(message="删除成功")


@router.get("/group/{group_name}")
async def get_settings_by_group(
    group_name: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """按分组获取设置"""
    try:
        group_enum = SettingGroup(group_name)
    except ValueError:
        from app.exceptions import ValidationError
        raise ValidationError(f"无效的分组: {group_name}")
    
    settings = await setting_service.get_by_group(db, group_enum)
    return success_response({
        s.key: {
            "value": s.value,
            "description": s.description
        }
        for s in settings
    })


# 快捷接口
@router.get("/wechat/config")
async def get_wechat_config(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """获取微信配置"""
    config = await setting_service.get_wechat_settings(db)
    return success_response(config)


@router.get("/payment/config")
async def get_payment_config(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """获取支付配置"""
    config = await setting_service.get_payment_settings(db)
    return success_response(config)


@router.get("/sms/config")
async def get_sms_config(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """获取短信配置"""
    config = await setting_service.get_sms_settings(db)
    return success_response(config)
