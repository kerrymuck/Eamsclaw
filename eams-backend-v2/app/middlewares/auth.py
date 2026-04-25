from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import get_settings
from app.exceptions import AuthenticationError

settings = get_settings()
security = HTTPBearer(auto_error=False)


async def verify_token(credentials: HTTPAuthorizationCredentials = None) -> dict:
    """验证JWT Token"""
    if not credentials:
        raise AuthenticationError("缺少认证信息")
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("无效的认证信息")
        return payload
    except JWTError:
        raise AuthenticationError("认证已过期或无效")


async def get_current_user(request: Request) -> dict:
    """获取当前用户"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise AuthenticationError("缺少认证信息")
    
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer":
        raise AuthenticationError("无效的认证方式")
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise AuthenticationError("认证已过期或无效")


async def require_super_admin(request: Request) -> dict:
    """要求超级管理员权限"""
    user = await get_current_user(request)
    if user.get("role") != "super_admin":
        from app.exceptions import PermissionDenied
        raise PermissionDenied("需要超级管理员权限")
    return user


async def require_provider(request: Request) -> dict:
    """要求服务商权限"""
    user = await get_current_user(request)
    if user.get("role") not in ["provider", "super_admin"]:
        from app.exceptions import PermissionDenied
        raise PermissionDenied("需要服务商权限")
    return user


async def require_merchant(request: Request) -> dict:
    """要求商家权限"""
    user = await get_current_user(request)
    if user.get("role") not in ["merchant", "provider", "super_admin"]:
        from app.exceptions import PermissionDenied
        raise PermissionDenied("需要商家权限")
    return user
