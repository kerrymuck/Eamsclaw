from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from typing import Optional, List
from datetime import datetime
import uuid

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.user import User, Shop, ShopMember
from app.models.knowledge import Knowledge, KnowledgeCategory

router = APIRouter()


# ============ 知识库分类 ============

@router.get("/categories")
async def list_categories(
    shop_id: str,
    parent_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取知识库分类列表"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == shop.id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该店铺")
    
    # 查询分类
    query = select(KnowledgeCategory).where(KnowledgeCategory.shop_id == uuid.UUID(shop_id))
    if parent_id:
        query = query.where(KnowledgeCategory.parent_id == uuid.UUID(parent_id))
    else:
        query = query.where(KnowledgeCategory.parent_id.is_(None))
    
    query = query.order_by(KnowledgeCategory.sort_order)
    result = await db.execute(query)
    categories = result.scalars().all()
    
    return {
        "categories": [
            {
                "id": str(cat.id),
                "name": cat.name,
                "description": cat.description,
                "sort_order": cat.sort_order,
                "created_at": cat.created_at
            }
            for cat in categories
        ]
    }


@router.post("/categories")
async def create_category(
    shop_id: str,
    name: str,
    description: Optional[str] = None,
    parent_id: Optional[str] = None,
    sort_order: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建知识库分类"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == shop.id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该店铺")
    
    category = KnowledgeCategory(
        shop_id=uuid.UUID(shop_id),
        parent_id=uuid.UUID(parent_id) if parent_id else None,
        name=name,
        description=description,
        sort_order=sort_order
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return {
        "id": str(category.id),
        "name": category.name,
        "message": "分类创建成功"
    }


@router.put("/categories/{category_id}")
async def update_category(
    category_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    sort_order: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新知识库分类"""
    result = await db.execute(
        select(KnowledgeCategory).where(KnowledgeCategory.id == uuid.UUID(category_id))
    )
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == category.shop_id))
    shop = shop_result.scalar_one_or_none()
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == category.shop_id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问")
    
    if name:
        category.name = name
    if description is not None:
        category.description = description
    if sort_order is not None:
        category.sort_order = sort_order
    
    await db.commit()
    await db.refresh(category)
    
    return {"message": "分类更新成功"}


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除知识库分类"""
    result = await db.execute(
        select(KnowledgeCategory).where(KnowledgeCategory.id == uuid.UUID(category_id))
    )
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == category.shop_id))
    shop = shop_result.scalar_one_or_none()
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == category.shop_id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问")
    
    await db.delete(category)
    await db.commit()
    
    return {"message": "分类删除成功"}


# ============ 知识库条目 ============

@router.get("/knowledges")
async def list_knowledges(
    shop_id: str,
    category_id: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取知识库列表"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == shop.id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该店铺")
    
    # 构建查询
    query = select(Knowledge).where(Knowledge.shop_id == uuid.UUID(shop_id))
    
    if category_id:
        query = query.where(Knowledge.category_id == uuid.UUID(category_id))
    if status:
        query = query.where(Knowledge.status == status)
    if search:
        query = query.where(
            or_(
                Knowledge.question.ilike(f"%{search}%"),
                Knowledge.answer.ilike(f"%{search}%"),
                Knowledge.keywords.any(search)
            )
        )
    
    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页查询
    query = query.order_by(desc(Knowledge.priority), desc(Knowledge.hit_count))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    knowledges = result.scalars().all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "knowledges": [
            {
                "id": str(k.id),
                "category_id": str(k.category_id) if k.category_id else None,
                "question": k.question,
                "answer": k.answer[:200] + "..." if len(k.answer) > 200 else k.answer,
                "keywords": k.keywords,
                "hit_count": k.hit_count,
                "status": k.status,
                "priority": k.priority,
                "created_at": k.created_at
            }
            for k in knowledges
        ]
    }


@router.get("/knowledges/{knowledge_id}")
async def get_knowledge(
    knowledge_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取知识库详情"""
    result = await db.execute(
        select(Knowledge).where(Knowledge.id == uuid.UUID(knowledge_id))
    )
    knowledge = result.scalar_one_or_none()
    
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识库条目不存在")
    
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == knowledge.shop_id))
    shop = shop_result.scalar_one_or_none()
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == knowledge.shop_id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问")
    
    return {
        "id": str(knowledge.id),
        "shop_id": str(knowledge.shop_id),
        "category_id": str(knowledge.category_id) if knowledge.category_id else None,
        "question": knowledge.question,
        "answer": knowledge.answer,
        "answer_html": knowledge.answer_html,
        "keywords": knowledge.keywords,
        "similar_questions": knowledge.similar_questions,
        "hit_count": knowledge.hit_count,
        "last_hit_at": knowledge.last_hit_at,
        "status": knowledge.status,
        "priority": knowledge.priority,
        "related_knowledge_ids": [str(id) for id in knowledge.related_knowledge_ids] if knowledge.related_knowledge_ids else [],
        "attachments": knowledge.attachments,
        "created_at": knowledge.created_at,
        "updated_at": knowledge.updated_at
    }


@router.post("/knowledges")
async def create_knowledge(
    shop_id: str,
    question: str,
    answer: str,
    category_id: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    similar_questions: Optional[List[str]] = None,
    priority: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建知识库条目"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == shop.id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该店铺")
    
    knowledge = Knowledge(
        shop_id=uuid.UUID(shop_id),
        category_id=uuid.UUID(category_id) if category_id else None,
        question=question,
        answer=answer,
        keywords=keywords or [],
        similar_questions=similar_questions or [],
        priority=priority,
        created_by=current_user.id,
        updated_by=current_user.id
    )
    db.add(knowledge)
    await db.commit()
    await db.refresh(knowledge)
    
    return {
        "id": str(knowledge.id),
        "question": knowledge.question,
        "message": "知识库条目创建成功"
    }


@router.put("/knowledges/{knowledge_id}")
async def update_knowledge(
    knowledge_id: str,
    question: Optional[str] = None,
    answer: Optional[str] = None,
    category_id: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    similar_questions: Optional[List[str]] = None,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新知识库条目"""
    result = await db.execute(
        select(Knowledge).where(Knowledge.id == uuid.UUID(knowledge_id))
    )
    knowledge = result.scalar_one_or_none()
    
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识库条目不存在")
    
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == knowledge.shop_id))
    shop = shop_result.scalar_one_or_none()
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == knowledge.shop_id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问")
    
    if question:
        knowledge.question = question
    if answer:
        knowledge.answer = answer
    if category_id is not None:
        knowledge.category_id = uuid.UUID(category_id) if category_id else None
    if keywords is not None:
        knowledge.keywords = keywords
    if similar_questions is not None:
        knowledge.similar_questions = similar_questions
    if status:
        knowledge.status = status
    if priority is not None:
        knowledge.priority = priority
    
    knowledge.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(knowledge)
    
    return {"message": "知识库条目更新成功"}


@router.delete("/knowledges/{knowledge_id}")
async def delete_knowledge(
    knowledge_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除知识库条目"""
    result = await db.execute(
        select(Knowledge).where(Knowledge.id == uuid.UUID(knowledge_id))
    )
    knowledge = result.scalar_one_or_none()
    
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识库条目不存在")
    
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == knowledge.shop_id))
    shop = shop_result.scalar_one_or_none()
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == knowledge.shop_id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问")
    
    await db.delete(knowledge)
    await db.commit()
    
    return {"message": "知识库条目删除成功"}


# ============ 智能搜索 ============

@router.get("/search")
async def search_knowledge(
    shop_id: str,
    query: str,
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """智能搜索知识库"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == shop.id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该店铺")
    
    # 搜索知识库
    search_query = select(Knowledge).where(
        and_(
            Knowledge.shop_id == uuid.UUID(shop_id),
            Knowledge.status == 'active',
            or_(
                Knowledge.question.ilike(f"%{query}%"),
                Knowledge.answer.ilike(f"%{query}%"),
                Knowledge.keywords.any(query)
            )
        )
    ).order_by(desc(Knowledge.priority)).limit(limit)
    
    result = await db.execute(search_query)
    knowledges = result.scalars().all()
    
    return {
        "query": query,
        "results": [
            {
                "id": str(k.id),
                "question": k.question,
                "answer": k.answer,
                "similarity": 0.9  # 简化版本，实际使用向量相似度
            }
            for k in knowledges
        ]
    }
