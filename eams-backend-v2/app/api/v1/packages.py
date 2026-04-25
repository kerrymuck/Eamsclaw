from fastapi import APIRouter, Depends, Query
from typing import Optional
from pydantic import BaseModel
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.base import success_response
from app.middlewares.auth import require_super_admin, require_provider
from app.services.user import package_service

router = APIRouter()


class PackageCreate(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    price: Decimal
    original_price: Optional[Decimal] = None
    ai_tokens: int = 0
    ai_calls: int = 0
    validity_days: int = 30


class PackageUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    ai_tokens: Optional[int] = None
    ai_calls: Optional[int] = None
    validity_days: Optional[int] = None
    status: Optional[str] = None


@router.get("")
async def list_packages(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    provider_id: Optional[int] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """获取套餐列表（超管）"""
    skip = (page - 1) * page_size
    packages = await package_service.get_all(db, skip=skip, limit=page_size)
    total = await package_service.count(db)
    
    return success_response({
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "items": [p.to_dict() for p in packages]
    })


@router.post("")
async def create_package(
    data: PackageCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """创建套餐（超管）"""
    package = await package_service.create(db, **data.dict())
    return success_response(package.to_dict(), message="创建成功")


@router.get("/{package_id}")
async def get_package(
    package_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """获取套餐详情"""
    package = await package_service.get_by_id(db, package_id)
    if not package:
        from app.exceptions import NotFoundError
        raise NotFoundError("套餐不存在")
    return success_response(package.to_dict())


@router.put("/{package_id}")
async def update_package(
    package_id: int,
    data: PackageUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """更新套餐"""
    package = await package_service.update(db, package_id, **data.dict(exclude_unset=True))
    if not package:
        from app.exceptions import NotFoundError
        raise NotFoundError("套餐不存在")
    return success_response(package.to_dict(), message="更新成功")


@router.delete("/{package_id}")
async def delete_package(
    package_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """删除套餐"""
    result = await package_service.delete(db, package_id)
    if not result:
        from app.exceptions import NotFoundError
        raise NotFoundError("套餐不存在")
    return success_response(message="删除成功")


# 服务商视角
@router.get("/provider/my")
async def list_my_packages(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_provider)
):
    """获取我的套餐列表（服务商）"""
    # TODO: 从token获取服务商ID
    provider_id = 1
    skip = (page - 1) * page_size
    packages = await package_service.get_by_provider(db, provider_id, skip, page_size)
    
    return success_response({
        "total": len(packages),
        "page": page,
        "page_size": page_size,
        "pages": 1,
        "items": [p.to_dict() for p in packages]
    })


@router.post("/provider/create")
async def create_provider_package(
    data: PackageCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_provider)
):
    """创建套餐（服务商）"""
    # TODO: 从token获取服务商ID
    provider_id = 1
    package = await package_service.create(db, provider_id=provider_id, **data.dict())
    return success_response(package.to_dict(), message="创建成功")
