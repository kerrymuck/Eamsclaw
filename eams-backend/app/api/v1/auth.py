from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
import uuid

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, Shop, ShopMember

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if current_user.status != 'active':
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


# ============ 认证接口 ============

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    # 查询用户
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != 'active':
        raise HTTPException(status_code=400, detail="用户已被禁用")
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # 创建token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "real_name": user.real_name,
            "avatar_url": user.avatar_url
        }
    }


@router.post("/register")
async def register(
    username: str,
    password: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    real_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否已存在
    if email:
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    # 创建用户
    user = User(
        username=username,
        password_hash=get_password_hash(password),
        email=email,
        phone=phone,
        real_name=real_name,
        role='admin'  # 第一个用户设为管理员
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "message": "注册成功"
    }


@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_active_user)):
    """刷新Token"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user.id)}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "real_name": current_user.real_name,
        "avatar_url": current_user.avatar_url,
        "role": current_user.role,
        "status": current_user.status,
        "last_login_at": current_user.last_login_at,
        "created_at": current_user.created_at
    }


@router.put("/me")
async def update_me(
    email: Optional[str] = None,
    phone: Optional[str] = None,
    real_name: Optional[str] = None,
    avatar_url: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户信息"""
    if email:
        current_user.email = email
    if phone:
        current_user.phone = phone
    if real_name:
        current_user.real_name = real_name
    if avatar_url:
        current_user.avatar_url = avatar_url
    
    await db.commit()
    await db.refresh(current_user)
    
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "real_name": current_user.real_name,
        "avatar_url": current_user.avatar_url,
        "message": "更新成功"
    }


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    
    current_user.password_hash = get_password_hash(new_password)
    await db.commit()
    
    return {"message": "密码修改成功"}


# ============ 店铺管理 ============

@router.get("/shops")
async def list_shops(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户店铺列表"""
    # 获取用户拥有的店铺
    owned_result = await db.execute(
        select(Shop).where(Shop.owner_id == current_user.id)
    )
    owned_shops = owned_result.scalars().all()
    
    # 获取用户作为成员的店铺
    member_result = await db.execute(
        select(Shop, ShopMember.role)
        .join(ShopMember, Shop.id == ShopMember.shop_id)
        .where(ShopMember.user_id == current_user.id)
    )
    member_shops = member_result.all()
    
    return {
        "owned": [
            {
                "id": str(shop.id),
                "name": shop.name,
                "description": shop.description,
                "status": shop.status,
                "created_at": shop.created_at
            }
            for shop in owned_shops
        ],
        "member": [
            {
                "id": str(shop.id),
                "name": shop.name,
                "description": shop.description,
                "status": shop.status,
                "role": role,
                "created_at": shop.created_at
            }
            for shop, role in member_shops
        ]
    }


@router.post("/shops")
async def create_shop(
    name: str,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建店铺"""
    shop = Shop(
        name=name,
        description=description,
        owner_id=current_user.id
    )
    db.add(shop)
    await db.commit()
    await db.refresh(shop)
    
    return {
        "id": str(shop.id),
        "name": shop.name,
        "description": shop.description,
        "status": shop.status,
        "message": "店铺创建成功"
    }


@router.get("/shops/{shop_id}")
async def get_shop(
    shop_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取店铺详情"""
    result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    # 检查权限
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == shop.id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该店铺")
    
    return {
        "id": str(shop.id),
        "name": shop.name,
        "description": shop.description,
        "status": shop.status,
        "settings": shop.settings,
        "created_at": shop.created_at,
        "updated_at": shop.updated_at
    }


@router.put("/shops/{shop_id}")
async def update_shop(
    shop_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    settings: Optional[dict] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新店铺信息"""
    result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    # 检查权限（只有店主可以修改）
    if shop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有店主可以修改店铺信息")
    
    if name:
        shop.name = name
    if description:
        shop.description = description
    if settings:
        shop.settings = settings
    
    await db.commit()
    await db.refresh(shop)
    
    return {
        "id": str(shop.id),
        "name": shop.name,
        "description": shop.description,
        "settings": shop.settings,
        "message": "店铺更新成功"
    }


# ============ 成员管理 ============

@router.get("/shops/{shop_id}/members")
async def list_shop_members(
    shop_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取店铺成员列表"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    # 检查访问权限
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == shop.id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该店铺")
    
    # 获取成员列表
    members_result = await db.execute(
        select(ShopMember, User)
        .join(User, ShopMember.user_id == User.id)
        .where(ShopMember.shop_id == uuid.UUID(shop_id))
    )
    members = members_result.all()
    
    return {
        "members": [
            {
                "id": str(member.id),
                "user_id": str(user.id),
                "username": user.username,
                "real_name": user.real_name,
                "avatar_url": user.avatar_url,
                "role": member.role,
                "created_at": member.created_at
            }
            for member, user in members
        ]
    }


@router.post("/shops/{shop_id}/members")
async def add_shop_member(
    shop_id: str,
    username: str,
    role: str = 'member',
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """添加店铺成员"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    # 只有店主可以添加成员
    if shop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有店主可以添加成员")
    
    # 查找用户
    user_result = await db.execute(select(User).where(User.username == username))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查是否已是成员
    existing_result = await db.execute(
        select(ShopMember).where(
            ShopMember.shop_id == shop.id,
            ShopMember.user_id == user.id
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该用户已是店铺成员")
    
    # 创建成员关系
    member = ShopMember(
        shop_id=shop.id,
        user_id=user.id,
        role=role
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    
    return {
        "id": str(member.id),
        "user_id": str(user.id),
        "username": user.username,
        "role": member.role,
        "message": "成员添加成功"
    }


@router.delete("/shops/{shop_id}/members/{user_id}")
async def remove_shop_member(
    shop_id: str,
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """移除店铺成员"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    # 只有店主可以移除成员（不能移除自己）
    if shop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有店主可以移除成员")
    
    # 不能移除店主自己
    if str(shop.owner_id) == user_id:
        raise HTTPException(status_code=400, detail="不能移除店主")
    
    # 查找并删除成员关系
    member_result = await db.execute(
        select(ShopMember).where(
            ShopMember.shop_id == uuid.UUID(shop_id),
            ShopMember.user_id == uuid.UUID(user_id)
        )
    )
    member = member_result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    await db.delete(member)
    await db.commit()
    
    return {"message": "成员移除成功"}
