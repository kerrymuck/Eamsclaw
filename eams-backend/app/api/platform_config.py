"""
平台配置API路由
管理各电商平台的API配置和授权
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.models import PlatformConfig, ShopPlatformAuth, Shop, User
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/platform-configs", tags=["平台配置"])


# ============ 请求/响应模型 ============

class APIConfig(BaseModel):
    app_key: str
    app_secret: str
    api_base_url: str
    auth_url: Optional[str] = None
    token_url: Optional[str] = None
    webhook_secret: Optional[str] = None


class OAuthConfig(BaseModel):
    auth_type: str = "oauth2"
    scopes: List[str] = []
    callback_url: Optional[str] = None
    token_expire_seconds: int = 86400


class FeaturesConfig(BaseModel):
    support_message: bool = True
    support_order: bool = True
    support_logistics: bool = True
    support_product: bool = False
    support_webhook: bool = True


class PlatformConfigCreate(BaseModel):
    platform_type: str
    platform_name: str
    platform_category: str = "domestic"
    description: Optional[str] = None
    icon_url: Optional[str] = None
    api_config: APIConfig
    oauth_config: Optional[OAuthConfig] = None
    features: Optional[FeaturesConfig] = None


class PlatformConfigUpdate(BaseModel):
    platform_name: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    api_config: Optional[APIConfig] = None
    oauth_config: Optional[OAuthConfig] = None
    features: Optional[FeaturesConfig] = None
    is_enabled: Optional[bool] = None


class PlatformConfigResponse(BaseModel):
    id: str
    platform_type: str
    platform_name: str
    platform_category: str
    description: Optional[str]
    icon_url: Optional[str]
    features: dict
    is_enabled: bool
    is_system: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ShopPlatformAuthCreate(BaseModel):
    platform_config_id: str
    platform_shop_id: str
    platform_shop_name: Optional[str] = None
    auth_code: Optional[str] = None  # OAuth授权码


class ShopPlatformAuthResponse(BaseModel):
    id: str
    shop_id: str
    platform_config_id: str
    platform_type: str
    platform_name: str
    platform_shop_id: str
    platform_shop_name: Optional[str]
    platform_shop_logo: Optional[str]
    auth_status: str
    auth_error: Optional[str]
    authorized_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuthURLRequest(BaseModel):
    platform_config_id: str
    redirect_uri: Optional[str] = None


class AuthURLResponse(BaseModel):
    auth_url: str
    state: str


class RefreshTokenRequest(BaseModel):
    auth_id: str


# ============ 平台配置管理API ============

@router.get("/", response_model=List[PlatformConfigResponse])
async def list_platform_configs(
    category: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取平台配置列表"""
    query = db.query(PlatformConfig)
    
    if category:
        query = query.filter(PlatformConfig.platform_category == category)
    if is_enabled is not None:
        query = query.filter(PlatformConfig.is_enabled == is_enabled)
    
    configs = query.all()
    return configs


@router.get("/{config_id}", response_model=PlatformConfigResponse)
async def get_platform_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个平台配置"""
    config = db.query(PlatformConfig).filter(PlatformConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="平台配置不存在")
    return config


@router.post("/", response_model=PlatformConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_platform_config(
    data: PlatformConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建平台配置（管理员功能）"""
    # 检查是否已存在
    existing = db.query(PlatformConfig).filter(
        PlatformConfig.platform_type == data.platform_type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该平台配置已存在")
    
    config = PlatformConfig(
        platform_type=data.platform_type,
        platform_name=data.platform_name,
        platform_category=data.platform_category,
        description=data.description,
        icon_url=data.icon_url,
        api_config=data.api_config.dict(),
        oauth_config=data.oauth_config.dict() if data.oauth_config else {},
        features=data.features.dict() if data.features else {}
    )
    
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.put("/{config_id}", response_model=PlatformConfigResponse)
async def update_platform_config(
    config_id: str,
    data: PlatformConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新平台配置"""
    config = db.query(PlatformConfig).filter(PlatformConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="平台配置不存在")
    
    if config.is_system:
        raise HTTPException(status_code=403, detail="系统预设配置不可修改")
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    db.commit()
    db.refresh(config)
    return config


@router.delete("/{config_id}")
async def delete_platform_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除平台配置"""
    config = db.query(PlatformConfig).filter(PlatformConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="平台配置不存在")
    
    if config.is_system:
        raise HTTPException(status_code=403, detail="系统预设配置不可删除")
    
    db.delete(config)
    db.commit()
    return {"message": "删除成功"}


# ============ 店铺平台授权API ============

@router.get("/shops/{shop_id}/auths", response_model=List[ShopPlatformAuthResponse])
async def list_shop_platform_auths(
    shop_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取店铺的平台授权列表"""
    # 检查店铺权限
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    auths = db.query(ShopPlatformAuth).filter(
        ShopPlatformAuth.shop_id == shop_id
    ).all()
    
    # 补充平台信息
    result = []
    for auth in auths:
        config = db.query(PlatformConfig).filter(
            PlatformConfig.id == auth.platform_config_id
        ).first()
        auth.platform_type = config.platform_type if config else ""
        auth.platform_name = config.platform_name if config else ""
        result.append(auth)
    
    return result


@router.post("/shops/{shop_id}/auths", response_model=ShopPlatformAuthResponse)
async def create_shop_platform_auth(
    shop_id: str,
    data: ShopPlatformAuthCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建店铺平台授权"""
    # 检查店铺
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    # 检查平台配置
    config = db.query(PlatformConfig).filter(
        PlatformConfig.id == data.platform_config_id
    ).first()
    if not config:
        raise HTTPException(status_code=404, detail="平台配置不存在")
    
    # 检查是否已存在
    existing = db.query(ShopPlatformAuth).filter(
        ShopPlatformAuth.shop_id == shop_id,
        ShopPlatformAuth.platform_config_id == data.platform_config_id,
        ShopPlatformAuth.platform_shop_id == data.platform_shop_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该店铺授权已存在")
    
    auth = ShopPlatformAuth(
        shop_id=shop_id,
        platform_config_id=data.platform_config_id,
        platform_shop_id=data.platform_shop_id,
        platform_shop_name=data.platform_shop_name,
        auth_status='pending'
    )
    
    db.add(auth)
    db.commit()
    db.refresh(auth)
    
    auth.platform_type = config.platform_type
    auth.platform_name = config.platform_name
    
    return auth


@router.post("/shops/{shop_id}/auth-url", response_model=AuthURLResponse)
async def get_platform_auth_url(
    shop_id: str,
    data: AuthURLRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取平台授权URL
    用户点击后跳转到电商平台授权页面
    """
    # 检查平台配置
    config = db.query(PlatformConfig).filter(
        PlatformConfig.id == data.platform_config_id
    ).first()
    if not config:
        raise HTTPException(status_code=404, detail="平台配置不存在")
    
    api_config = config.api_config or {}
    oauth_config = config.oauth_config or {}
    
    # 生成授权URL（以OAuth2为例）
    import secrets
    state = secrets.token_urlsafe(32)
    
    auth_url = api_config.get('auth_url', '')
    app_key = api_config.get('app_key', '')
    redirect_uri = data.redirect_uri or oauth_config.get('callback_url', '')
    scopes = ' '.join(oauth_config.get('scopes', []))
    
    # 构建授权URL（各平台格式可能不同）
    from urllib.parse import urlencode
    params = {
        'response_type': 'code',
        'client_id': app_key,
        'redirect_uri': redirect_uri,
        'state': state,
        'scope': scopes
    }
    full_auth_url = f"{auth_url}?{urlencode(params)}"
    
    # TODO: 保存state到缓存，用于后续验证
    
    return AuthURLResponse(auth_url=full_auth_url, state=state)


@router.post("/shops/{shop_id}/auth-callback")
async def handle_platform_auth_callback(
    shop_id: str,
    code: str,
    state: str,
    platform_config_id: str,
    db: Session = Depends(get_db)
):
    """
    处理平台授权回调
    电商平台授权完成后回调此接口
    """
    # TODO: 验证state
    
    # 获取平台配置
    config = db.query(PlatformConfig).filter(
        PlatformConfig.id == platform_config_id
    ).first()
    if not config:
        raise HTTPException(status_code=404, detail="平台配置不存在")
    
    # TODO: 调用平台适配器获取access_token
    # from app.services.platform import PlatformAdapterRegistry
    # adapter = PlatformAdapterRegistry.get_adapter(config.platform_type)
    # auth_result = await adapter.authenticate(code)
    
    # 模拟授权结果
    auth_result = {
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "expire_in": 86400,
        "shop_info": {
            "shop_id": "platform_shop_123",
            "shop_name": "示例店铺"
        }
    }
    
    # 查找或创建授权记录
    auth = db.query(ShopPlatformAuth).filter(
        ShopPlatformAuth.shop_id == shop_id,
        ShopPlatformAuth.platform_config_id == platform_config_id
    ).first()
    
    if not auth:
        auth = ShopPlatformAuth(
            shop_id=shop_id,
            platform_config_id=platform_config_id,
            platform_shop_id=auth_result["shop_info"]["shop_id"],
            platform_shop_name=auth_result["shop_info"]["shop_name"]
        )
        db.add(auth)
    
    # 更新授权信息
    from datetime import timedelta
    auth.auth_status = 'authorized'
    auth.auth_credentials = {
        "access_token": auth_result["access_token"],
        "refresh_token": auth_result["refresh_token"],
        "token_type": "Bearer",
        "expires_at": (datetime.utcnow() + timedelta(seconds=auth_result["expire_in"])).isoformat()
    }
    auth.authorized_at = datetime.utcnow()
    auth.expires_at = datetime.utcnow() + timedelta(seconds=auth_result["expire_in"])
    
    db.commit()
    
    return {
        "message": "授权成功",
        "platform_shop_name": auth.platform_shop_name,
        "expires_at": auth.expires_at
    }


@router.post("/shops/{shop_id}/refresh-token")
async def refresh_platform_token(
    shop_id: str,
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """刷新平台授权令牌"""
    auth = db.query(ShopPlatformAuth).filter(
        ShopPlatformAuth.id == data.auth_id,
        ShopPlatformAuth.shop_id == shop_id
    ).first()
    
    if not auth:
        raise HTTPException(status_code=404, detail="授权记录不存在")
    
    if auth.auth_status != 'authorized':
        raise HTTPException(status_code=400, detail="授权状态异常，无法刷新")
    
    # 获取平台配置
    config = db.query(PlatformConfig).filter(
        PlatformConfig.id == auth.platform_config_id
    ).first()
    
    # TODO: 调用平台适配器刷新token
    # from app.services.platform import PlatformAdapterRegistry
    # adapter = PlatformAdapterRegistry.get_adapter(config.platform_type)
    # refresh_result = await adapter.refresh_token(auth.auth_credentials.get('refresh_token'))
    
    # 模拟刷新结果
    from datetime import timedelta
    auth.auth_credentials["access_token"] = "new_mock_access_token"
    auth.auth_credentials["expires_at"] = (datetime.utcnow() + timedelta(days=1)).isoformat()
    auth.expires_at = datetime.utcnow() + timedelta(days=1)
    auth.refreshed_at = datetime.utcnow()
    auth.refresh_count += 1
    
    db.commit()
    
    return {
        "message": "刷新成功",
        "expires_at": auth.expires_at
    }


@router.delete("/shops/{shop_id}/auths/{auth_id}")
async def revoke_platform_auth(
    shop_id: str,
    auth_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """撤销平台授权"""
    auth = db.query(ShopPlatformAuth).filter(
        ShopPlatformAuth.id == auth_id,
        ShopPlatformAuth.shop_id == shop_id
    ).first()
    
    if not auth:
        raise HTTPException(status_code=404, detail="授权记录不存在")
    
    # TODO: 调用平台API撤销授权
    
    auth.auth_status = 'revoked'
    auth.is_active = False
    db.commit()
    
    return {"message": "授权已撤销"}
