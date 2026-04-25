from fastapi import APIRouter, Depends, Query
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.base import success_response
from app.middlewares.auth import require_super_admin, require_provider
from app.services.user import merchant_service, provider_service

router = APIRouter()


class MerchantCreate(BaseModel):
    name: str
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None


class MerchantUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    status: Optional[str] = None


@router.get("")
async def list_merchants(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """获取商户列表（超管）"""
    skip = (page - 1) * page_size
    merchants = await merchant_service.get_all(db, skip=skip, limit=page_size)
    total = await merchant_service.count(db)
    
    return success_response({
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "items": [m.to_dict() for m in merchants]
    })


@router.post("")
async def create_merchant(
    data: MerchantCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """创建商户（超管）"""
    merchant = await merchant_service.create(db, **data.dict())
    return success_response(merchant.to_dict(), message="创建成功")


@router.get("/{merchant_id}")
async def get_merchant(
    merchant_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """获取商户详情"""
    merchant = await merchant_service.get_by_id(db, merchant_id)
    if not merchant:
        from app.exceptions import NotFoundError
        raise NotFoundError("商户不存在")
    return success_response(merchant.to_dict())


@router.put("/{merchant_id}")
async def update_merchant(
    merchant_id: int,
    data: MerchantUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """更新商户信息"""
    merchant = await merchant_service.update(db, merchant_id, **data.dict(exclude_unset=True))
    if not merchant:
        from app.exceptions import NotFoundError
        raise NotFoundError("商户不存在")
    return success_response(merchant.to_dict(), message="更新成功")


@router.delete("/{merchant_id}")
async def delete_merchant(
    merchant_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_super_admin)
):
    """删除商户"""
    result = await merchant_service.delete(db, merchant_id)
    if not result:
        from app.exceptions import NotFoundError
        raise NotFoundError("商户不存在")
    return success_response(message="删除成功")


# 服务商视角的商户管理
@router.get("/provider/list")
async def list_provider_merchants(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_provider)
):
    """获取服务商下的商户列表"""
    # TODO: 从token获取服务商ID
    provider_id = 1
    skip = (page - 1) * page_size
    merchants = await merchant_service.get_by_provider(db, provider_id, skip, page_size)
    
    return success_response({
        "total": len(merchants),
        "page": page,
        "page_size": page_size,
        "pages": 1,
        "items": [m.to_dict() for m in merchants]
    })
