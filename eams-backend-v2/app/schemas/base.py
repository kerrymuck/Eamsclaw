from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ResponseModel(BaseModel):
    """统一响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None
    timestamp: datetime = datetime.now()


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = 1
    page_size: int = 10


class PaginationResponse(BaseModel):
    """分页响应"""
    total: int
    page: int
    page_size: int
    pages: int
    items: list


def success_response(data: any = None, message: str = "success") -> dict:
    """成功响应"""
    return {
        "code": 200,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }


def error_response(code: int = 500, message: str = "error", data: any = None) -> dict:
    """错误响应"""
    return {
        "code": code,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
