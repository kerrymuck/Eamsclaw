from fastapi import HTTPException, status
from typing import Any, Optional


class BaseException(HTTPException):
    """基础异常类"""
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[dict] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class AuthenticationError(BaseException):
    """认证错误"""
    def __init__(self, detail: str = "认证失败"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class PermissionDenied(BaseException):
    """权限不足"""
    def __init__(self, detail: str = "权限不足"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class NotFoundError(BaseException):
    """资源不存在"""
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ValidationError(BaseException):
    """参数验证错误"""
    def __init__(self, detail: str = "参数验证失败"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class BusinessError(BaseException):
    """业务逻辑错误"""
    def __init__(self, detail: str = "业务处理失败"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class RateLimitError(BaseException):
    """请求频率限制"""
    def __init__(self, detail: str = "请求过于频繁"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        )
