"""
认证模块
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_user_ws(token: str, db: AsyncSession):
    """
    WebSocket认证
    验证JWT令牌并返回用户信息
    """
    # TODO: 实现JWT验证
    # 临时返回测试用户
    class MockUser:
        id = 1
        username = "admin"
        shop_id = 1
    
    return MockUser()


async def get_current_user(token: str, db: AsyncSession):
    """REST API认证"""
    return await get_current_user_ws(token, db)
