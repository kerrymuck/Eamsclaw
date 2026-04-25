"""
系统设置API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user
from app.models.system_setting import SystemSetting
import uuid

router = APIRouter()


class SettingItem(BaseModel):
    """设置项"""
    key: str
    value: Optional[str] = None
    group: str = 'general'
    description: Optional[str] = None
    is_encrypted: bool = False


class SettingResponse(BaseModel):
    """设置响应"""
    key: str
    value: Optional[str] = None
    group: str
    description: Optional[str] = None


class SettingsBatchUpdate(BaseModel):
    """批量更新设置"""
    settings: Dict[str, str]  # key -> value
    group: str = 'general'


@router.get("/settings", response_model=List[SettingResponse])
async def get_settings(
    group: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取系统设置列表"""
    query = db.query(SystemSetting)
    if group:
        query = query.filter(SystemSetting.setting_group == group)
    
    settings = query.all()
    return [
        SettingResponse(
            key=s.setting_key,
            value=s.setting_value,
            group=s.setting_group,
            description=s.description
        )
        for s in settings
    ]


@router.get("/settings/{key}", response_model=SettingResponse)
async def get_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取单个设置项"""
    setting = db.query(SystemSetting).filter(
        SystemSetting.setting_key == key
    ).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="设置项不存在")
    
    return SettingResponse(
        key=setting.setting_key,
        value=setting.setting_value,
        group=setting.setting_group,
        description=setting.description
    )


@router.post("/settings")
async def create_or_update_setting(
    item: SettingItem,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建或更新设置项"""
    setting = db.query(SystemSetting).filter(
        SystemSetting.setting_key == item.key
    ).first()
    
    if setting:
        # 更新
        setting.setting_value = item.value
        setting.setting_group = item.group
        setting.description = item.description
        setting.is_encrypted = item.is_encrypted
    else:
        # 创建
        setting = SystemSetting(
            id=str(uuid.uuid4()),
            setting_key=item.key,
            setting_value=item.value,
            setting_group=item.group,
            description=item.description,
            is_encrypted=item.is_encrypted
        )
        db.add(setting)
    
    db.commit()
    db.refresh(setting)
    
    return {"success": True, "message": "保存成功"}


@router.post("/settings/batch")
async def batch_update_settings(
    data: SettingsBatchUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """批量更新设置"""
    for key, value in data.settings.items():
        setting = db.query(SystemSetting).filter(
            SystemSetting.setting_key == key
        ).first()
        
        if setting:
            setting.setting_value = value
        else:
            setting = SystemSetting(
                id=str(uuid.uuid4()),
                setting_key=key,
                setting_value=value,
                setting_group=data.group
            )
            db.add(setting)
    
    db.commit()
    return {"success": True, "message": f"成功更新 {len(data.settings)} 个设置项"}


@router.get("/settings/group/{group_name}")
async def get_settings_by_group(
    group_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """按分组获取设置（返回键值对格式）"""
    settings = db.query(SystemSetting).filter(
        SystemSetting.setting_group == group_name
    ).all()
    
    return {
        s.setting_key: s.setting_value
        for s in settings
    }


@router.delete("/settings/{key}")
async def delete_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除设置项"""
    setting = db.query(SystemSetting).filter(
        SystemSetting.setting_key == key
    ).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="设置项不存在")
    
    db.delete(setting)
    db.commit()
    
    return {"success": True, "message": "删除成功"}