from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.schemas.base import success_response
from app.exceptions import AuthenticationError, ValidationError
from app.services.user import user_service
from app.utils.security import verify_password, create_access_token, create_refresh_token

router = APIRouter()
settings = get_settings()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    # 从数据库验证用户
    user = await user_service.get_by_username(db, request.username)
    
    if not user or not verify_password(request.password, user.password_hash):
        raise AuthenticationError("用户名或密码错误")
    
    token_data = {"sub": str(user.id), "username": user.username, "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return success_response({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role.value,
            "email": user.email
        }
    })


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """刷新访问令牌"""
    from jose import jwt, JWTError
    try:
        payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise AuthenticationError("无效的刷新令牌")
        
        token_data = {"sub": payload["sub"], "username": payload["username"], "role": payload["role"]}
        access_token = create_access_token(token_data)
        return success_response({
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        })
    except JWTError:
        raise AuthenticationError("刷新令牌已过期")


@router.get("/me")
async def get_current_user_info(request: Request):
    """获取当前用户信息"""
    # TODO: 从token解析用户信息
    return success_response({
        "id": 1,
        "username": "admin",
        "role": "super_admin",
        "email": "admin@example.com"
    })


@router.post("/logout")
async def logout():
    """用户登出"""
    # TODO: 将token加入黑名单
    return success_response(message="登出成功")
