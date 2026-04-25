from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户"""
    # TODO: 实现JWT验证
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 临时返回
    return {"id": "test-user", "username": "admin", "role": "admin"}


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """获取当前活跃用户"""
    # TODO: 检查用户状态
    return current_user


def get_current_shop(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """获取当前商户（临时实现）"""
    from sqlalchemy import text
    
    # 使用原始SQL查询，避免ORM关系问题
    result = db.execute(text("SELECT id, name FROM shops LIMIT 1")).fetchone()
    
    if not result:
        # 如果没有商户，创建一个测试商户
        from uuid import uuid4
        shop_id = str(uuid4())
        db.execute(text(
            "INSERT INTO shops (id, name, owner_id, status, created_at, updated_at) VALUES (:id, :name, :owner_id, :status, datetime('now'), datetime('now'))"
        ), {
            'id': shop_id,
            'name': '测试商户',
            'owner_id': 'test-user',
            'status': 'active'
        })
        db.commit()
        result = db.execute(text("SELECT id, name FROM shops WHERE id = :id"), {'id': shop_id}).fetchone()
    
    # 返回一个简单的对象
    class SimpleShop:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    return SimpleShop(result[0], result[1])
