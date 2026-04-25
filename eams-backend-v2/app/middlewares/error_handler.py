from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions import BaseException


async def exception_handler(request: Request, exc: BaseException):
    """全局异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )


async def global_exception_handler(request: Request, exc: Exception):
    """全局未知异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": None
        }
    )
