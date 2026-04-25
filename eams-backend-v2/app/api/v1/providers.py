from fastapi import APIRouter, Depends, Query
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.base import success_response
from app.middlewares.auth import require_super_admin
from app.services.user import provider_service

router = APIRouter()


class ProviderCreate(BaseModel):
    name: str
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None


class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    status: Optional[str] = None


@router.get("")
async def list_providers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """获取服务商列表"""
    skip = (page - 1) * page_size
    providers = await provider_service.get_all(db, skip=skip, limit=page_size)
    total = await provider_service.count(db)
    
    return success_response({
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "items": [p.to_dict() for p in providers]
    })


@router.post("")
async def create_provider(
    data: ProviderCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """创建服务商"""
    provider = await provider_service.create(db, **data.dict())
    return success_response(provider.to_dict(), message="创建成功")


@router.get("/{provider_id}")
async def get_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """获取服务商详情"""
    provider = await provider_service.get_by_id(db, provider_id)
    if not provider:
        from app.exceptions import NotFoundError
        raise NotFoundError("服务商不存在")
    return success_response(provider.to_dict())


@router.put("/{provider_id}")
async def update_provider(
    provider_id: int,
    data: ProviderUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """更新服务商"""
    provider = await provider_service.update(db, provider_id, **data.dict(exclude_unset=True))
    if not provider:
        from app.exceptions import NotFoundError
        raise NotFoundError("服务商不存在")
    return success_response(provider.to_dict(), message="更新成功")


@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """删除服务商"""
    result = await provider_service.delete(db, provider_id)
    if not result:
        from app.exceptions import NotFoundError
        raise NotFoundError("服务商不存在")
    return success_response(message="删除成功")
