from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from typing import Optional, List
from datetime import datetime
import uuid
import json

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.user import User, Shop, ShopMember
from app.models.conversation import Conversation, Message, Handoff

router = APIRouter()


# ============ 对话管理 ============

@router.get("/conversations")
async def list_conversations(
    shop_id: str,
    status: Optional[str] = None,
    platform_type: Optional[str] = None,
    assigned_to: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取对话列表"""
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
    
    # 构建查询
    query = select(Conversation).where(Conversation.shop_id == uuid.UUID(shop_id))
    
    if status:
        query = query.where(Conversation.status == status)
    if platform_type:
        query = query.where(Conversation.platform_type == platform_type)
    if assigned_to:
        if assigned_to == 'me':
            query = query.where(Conversation.assigned_to == current_user.id)
        elif assigned_to == 'unassigned':
            query = query.where(Conversation.assigned_to.is_(None))
        else:
            query = query.where(Conversation.assigned_to == uuid.UUID(assigned_to))
    if search:
        query = query.where(
            or_(
                Conversation.platform_user_name.ilike(f"%{search}%"),
                Conversation.last_message_preview.ilike(f"%{search}%")
            )
        )
    
    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页查询
    query = query.order_by(desc(Conversation.last_message_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    conversations = result.scalars().all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "conversations": [
            {
                "id": str(conv.id),
                "platform_type": conv.platform_type,
                "platform_user_id": conv.platform_user_id,
                "platform_user_name": conv.platform_user_name,
                "platform_user_avatar": conv.platform_user_avatar,
                "status": conv.status,
                "priority": conv.priority,
                "tags": conv.tags,
                "unread_count": conv.unread_count,
                "last_message_at": conv.last_message_at,
                "last_message_preview": conv.last_message_preview,
                "assigned_to": str(conv.assigned_to) if conv.assigned_to else None,
                "created_at": conv.created_at
            }
            for conv in conversations
        ]
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取对话详情"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 检查店铺权限
    shop_result = await db.execute(
        select(Shop).where(Shop.id == conversation.shop_id)
    )
    shop = shop_result.scalar_one_or_none()
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == conversation.shop_id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该对话")
    
    return {
        "id": str(conversation.id),
        "shop_id": str(conversation.shop_id),
        "platform_id": str(conversation.platform_id) if conversation.platform_id else None,
        "platform_type": conversation.platform_type,
        "platform_user_id": conversation.platform_user_id,
        "platform_user_name": conversation.platform_user_name,
        "platform_user_avatar": conversation.platform_user_avatar,
        "status": conversation.status,
        "priority": conversation.priority,
        "tags": conversation.tags,
        "metadata": conversation.metadata,
        "unread_count": conversation.unread_count,
        "assigned_to": str(conversation.assigned_to) if conversation.assigned_to else None,
        "handoff_reason": conversation.handoff_reason,
        "handoff_note": conversation.handoff_note,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at
    }


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    before_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取对话消息"""
    # 检查对话权限
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 检查店铺权限
    shop_result = await db.execute(
        select(Shop).where(Shop.id == conversation.shop_id)
    )
    shop = shop_result.scalar_one_or_none()
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == conversation.shop_id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该对话")
    
    # 查询消息
    query = select(Message).where(
        Message.conversation_id == uuid.UUID(conversation_id)
    ).order_by(desc(Message.created_at))
    
    if before_id:
        query = query.where(Message.id < uuid.UUID(before_id))
    
    query = query.limit(limit)
    result = await db.execute(query)
    messages = result.scalars().all()
    
    # 重置未读数
    if conversation.unread_count > 0:
        conversation.unread_count = 0
        await db.commit()
    
    return {
        "messages": [
            {
                "id": str(msg.id),
                "direction": msg.direction,
                "msg_type": msg.msg_type,
                "content": msg.content,
                "content_html": msg.content_html,
                "attachments": msg.attachments,
                "sender_type": msg.sender_type,
                "sender_name": msg.sender_name,
                "status": msg.status,
                "created_at": msg.created_at
            }
            for msg in reversed(messages)
        ]
    }


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    content: str,
    msg_type: str = 'text',
    attachments: Optional[List[dict]] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """发送消息"""
    # 检查对话权限
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 检查店铺权限
    shop_result = await db.execute(
        select(Shop).where(Shop.id == conversation.shop_id)
    )
    shop = shop_result.scalar_one_or_none()
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == conversation.shop_id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该对话")
    
    # 创建消息
    message = Message(
        conversation_id=uuid.UUID(conversation_id),
        direction='out',
        msg_type=msg_type,
        content=content,
        sender_type='agent',
        sender_id=current_user.id,
        sender_name=current_user.real_name or current_user.username,
        attachments=attachments or []
    )
    db.add(message)
    
    # 更新对话
    conversation.last_message_at = datetime.utcnow()
    conversation.last_message_preview = content[:200] if len(content) > 200 else content
    conversation.status = 'active'
    
    await db.commit()
    await db.refresh(message)
    
    return {
        "id": str(message.id),
        "content": message.content,
        "status": message.status,
        "created_at": message.created_at
    }


@router.post("/conversations/{conversation_id}/assign")
async def assign_conversation(
    conversation_id: str,
    user_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """分配对话"""
    # 检查对话权限
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 检查店铺权限
    shop_result = await db.execute(
        select(Shop).where(Shop.id == conversation.shop_id)
    )
    shop = shop_result.scalar_one_or_none()
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == conversation.shop_id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该对话")
    
    # 分配对话
    if user_id:
        conversation.assigned_to = uuid.UUID(user_id)
    else:
        conversation.assigned_to = current_user.id
    
    await db.commit()
    
    return {
        "message": "对话已分配",
        "assigned_to": str(conversation.assigned_to)
    }


@router.post("/conversations/{conversation_id}/close")
async def close_conversation(
    conversation_id: str,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """关闭对话"""
    # 检查对话权限
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 检查店铺权限
    shop_result = await db.execute(
        select(Shop).where(Shop.id == conversation.shop_id)
    )
    shop = shop_result.scalar_one_or_none()
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == conversation.shop_id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该对话")
    
    # 关闭对话
    conversation.status = 'closed'
    conversation.closed_at = datetime.utcnow()
    conversation.closed_by = current_user.id
    conversation.close_reason = reason
    
    await db.commit()
    
    return {"message": "对话已关闭"}


@router.post("/conversations/{conversation_id}/tags")
async def update_tags(
    conversation_id: str,
    tags: List[str],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新对话标签"""
    # 检查对话权限
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 检查店铺权限
    shop_result = await db.execute(
        select(Shop).where(Shop.id == conversation.shop_id)
    )
    shop = shop_result.scalar_one_or_none()
    
    if shop.owner_id != current_user.id:
        member_result = await db.execute(
            select(ShopMember).where(
                ShopMember.shop_id == conversation.shop_id,
                ShopMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="无权访问该对话")
    
    conversation.tags = tags
    await db.commit()
    
    return {"message": "标签已更新", "tags": tags}


# ============ 转人工管理 ============

@router.get("/handoffs")
async def list_handoffs(
    shop_id: str,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取转人工列表"""
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
    
    # 查询转人工记录
    query = select(Handoff).where(Handoff.shop_id == uuid.UUID(shop_id))
    if status:
        query = query.where(Handoff.status == status)
    
    query = query.order_by(desc(Handoff.created_at))
    result = await db.execute(query)
    handoffs = result.scalars().all()
    
    return {
        "handoffs": [
            {
                "id": str(h.id),
                "conversation_id": str(h.conversation_id),
                "reason": h.reason,
                "note": h.note,
                "triggered_by": h.triggered_by,
                "status": h.status,
                "accepted_by": str(h.accepted_by) if h.accepted_by else None,
                "accepted_at": h.accepted_at,
                "created_at": h.created_at
            }
            for h in handoffs
        ]
    }


@router.post("/handoffs/{handoff_id}/accept")
async def accept_handoff(
    handoff_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """接受转人工"""
    result = await db.execute(
        select(Handoff).where(Handoff.id == uuid.UUID(handoff_id))
    )
    handoff = result.scalar_one_or_none()
    
    if not handoff:
        raise HTTPException(status_code=404, detail="转人工记录不存在")
    
    if handoff.status != 'pending':
        raise HTTPException(status_code=400, detail="该转人工已被处理")
    
    handoff.status = 'accepted'
    handoff.accepted_by = current_user.id
    handoff.accepted_at = datetime.utcnow()
    
    # 更新对话状态
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == handoff.conversation_id)
    )
    conversation = conv_result.scalar_one_or_none()
    if conversation:
        conversation.status = 'handled'
        conversation.assigned_to = current_user.id
    
    await db.commit()
    
    return {"message": "已接受转人工"}


@router.post("/handoffs/{handoff_id}/resolve")
async def resolve_handoff(
    handoff_id: str,
    note: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """解决转人工"""
    result = await db.execute(
        select(Handoff).where(Handoff.id == uuid.UUID(handoff_id))
    )
    handoff = result.scalar_one_or_none()
    
    if not handoff:
        raise HTTPException(status_code=404, detail="转人工记录不存在")
    
    handoff.status = 'resolved'
    handoff.resolved_at = datetime.utcnow()
    handoff.resolution_note = note
    
    await db.commit()
    
    return {"message": "转人工已解决"}
