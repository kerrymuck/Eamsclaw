from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import hmac
import hashlib
import json

from app.core.database import get_db
from app.core.config import settings
from app.api.v1.auth import get_current_active_user
from app.models.user import User, Shop, ShopMember, Platform
from app.models.conversation import Conversation, Message

router = APIRouter()


# ============ 平台店铺管理 ============

@router.get("/platforms")
async def list_platforms(
    shop_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取店铺绑定的平台列表"""
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
    
    # 查询平台绑定
    result = await db.execute(
        select(Platform).where(Platform.shop_id == uuid.UUID(shop_id))
    )
    platforms = result.scalars().all()
    
    return {
        "platforms": [
            {
                "id": str(p.id),
                "platform_type": p.platform_type,
                "platform_shop_id": p.platform_shop_id,
                "platform_shop_name": p.platform_shop_name,
                "auth_status": p.auth_status,
                "last_auth_at": p.last_auth_at,
                "expires_at": p.expires_at,
                "created_at": p.created_at
            }
            for p in platforms
        ]
    }


@router.post("/platforms/bind")
async def bind_platform(
    shop_id: str,
    platform_type: str,  # taobao, jd, pdd
    platform_shop_id: str,
    platform_shop_name: Optional[str] = None,
    auth_data: Optional[Dict] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """绑定电商平台"""
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == uuid.UUID(shop_id)))
    shop = shop_result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    if shop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有店主可以绑定平台")
    
    # 检查是否已绑定
    existing_result = await db.execute(
        select(Platform).where(
            Platform.shop_id == uuid.UUID(shop_id),
            Platform.platform_type == platform_type
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该平台已绑定")
    
    # 创建平台绑定
    platform = Platform(
        shop_id=uuid.UUID(shop_id),
        platform_type=platform_type,
        platform_shop_id=platform_shop_id,
        platform_shop_name=platform_shop_name,
        auth_status='pending',  # 待授权
        auth_data=auth_data or {}
    )
    db.add(platform)
    await db.commit()
    await db.refresh(platform)
    
    return {
        "id": str(platform.id),
        "platform_type": platform.platform_type,
        "auth_status": platform.auth_status,
        "message": "平台绑定已创建，请完成授权",
        "auth_url": f"/api/v1/platform/auth/{platform_type}?platform_id={platform.id}"
    }


@router.post("/platforms/{platform_id}/auth")
async def auth_platform(
    platform_id: str,
    auth_code: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """完成平台授权"""
    result = await db.execute(
        select(Platform).where(Platform.id == uuid.UUID(platform_id))
    )
    platform = result.scalar_one_or_none()
    
    if not platform:
        raise HTTPException(status_code=404, detail="平台绑定不存在")
    
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == platform.shop_id))
    shop = shop_result.scalar_one_or_none()
    
    if shop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有店主可以授权")
    
    # TODO: 调用平台API完成授权
    # 这里模拟授权成功
    platform.auth_status = 'active'
    platform.auth_data['auth_code'] = auth_code
    platform.last_auth_at = datetime.utcnow()
    await db.commit()
    
    return {
        "message": "平台授权成功",
        "platform_type": platform.platform_type,
        "auth_status": platform.auth_status
    }


@router.delete("/platforms/{platform_id}")
async def unbind_platform(
    platform_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """解绑平台"""
    result = await db.execute(
        select(Platform).where(Platform.id == uuid.UUID(platform_id))
    )
    platform = result.scalar_one_or_none()
    
    if not platform:
        raise HTTPException(status_code=404, detail="平台绑定不存在")
    
    # 检查店铺权限
    shop_result = await db.execute(select(Shop).where(Shop.id == platform.shop_id))
    shop = shop_result.scalar_one_or_none()
    
    if shop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有店主可以解绑")
    
    await db.delete(platform)
    await db.commit()
    
    return {"message": "平台解绑成功"}


# ============ 平台消息回调 ============

@router.post("/webhook/{platform_type}")
async def platform_webhook(
    platform_type: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """接收平台消息推送"""
    body = await request.body()
    
    # 根据平台类型处理
    if platform_type == 'taobao':
        return await handle_taobao_webhook(body, request.headers, db)
    elif platform_type == 'jd':
        return await handle_jd_webhook(body, request.headers, db)
    elif platform_type == 'pdd':
        return await handle_pdd_webhook(body, request.headers, db)
    else:
        raise HTTPException(status_code=400, detail="不支持的平台类型")


async def handle_taobao_webhook(body: bytes, headers: Dict, db: AsyncSession):
    """处理淘宝消息回调"""
    try:
        data = json.loads(body)
        
        # TODO: 验证签名
        # sign = headers.get('X-Taobao-Sign')
        
        msg_type = data.get('msg_type')
        
        if msg_type == 'message':
            # 处理用户消息
            await process_incoming_message(
                platform_type='taobao',
                platform_shop_id=data.get('seller_nick'),
                platform_user_id=data.get('buyer_nick'),
                platform_user_name=data.get('buyer_nick'),
                message_content=data.get('content'),
                platform_msg_id=data.get('msg_id'),
                db=db
            )
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def handle_jd_webhook(body: bytes, headers: Dict, db: AsyncSession):
    """处理京东消息回调"""
    try:
        data = json.loads(body)
        
        # TODO: 验证签名
        
        if data.get('type') == 'message':
            await process_incoming_message(
                platform_type='jd',
                platform_shop_id=data.get('shop_id'),
                platform_user_id=data.get('customer_id'),
                platform_user_name=data.get('customer_name'),
                message_content=data.get('content'),
                platform_msg_id=data.get('msg_id'),
                db=db
            )
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def handle_pdd_webhook(body: bytes, headers: Dict, db: AsyncSession):
    """处理拼多多消息回调"""
    try:
        data = json.loads(body)
        
        # TODO: 验证签名
        
        if data.get('cmd') == 'message':
            await process_incoming_message(
                platform_type='pdd',
                platform_shop_id=data.get('mall_id'),
                platform_user_id=data.get('user_id'),
                platform_user_name=data.get('user_name'),
                message_content=data.get('message'),
                platform_msg_id=data.get('msg_seq'),
                db=db
            )
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def process_incoming_message(
    platform_type: str,
    platform_shop_id: str,
    platform_user_id: str,
    platform_user_name: str,
    message_content: str,
    platform_msg_id: Optional[str] = None,
    db: AsyncSession = None
):
    """处理接收到的消息"""
    # 查找平台绑定
    result = await db.execute(
        select(Platform).where(
            Platform.platform_type == platform_type,
            Platform.platform_shop_id == platform_shop_id,
            Platform.auth_status == 'active'
        )
    )
    platform = result.scalar_one_or_none()
    
    if not platform:
        return {"error": "Platform not found or not active"}
    
    # 查找或创建对话
    conv_result = await db.execute(
        select(Conversation).where(
            Conversation.platform_id == platform.id,
            Conversation.platform_user_id == platform_user_id,
            Conversation.status.in_(['active', 'pending_handoff', 'handled'])
        )
    )
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        # 创建新对话
        conversation = Conversation(
            shop_id=platform.shop_id,
            platform_id=platform.id,
            platform_type=platform_type,
            platform_user_id=platform_user_id,
            platform_user_name=platform_user_name,
            status='active'
        )
        db.add(conversation)
        await db.flush()
    
    # 创建消息
    message = Message(
        conversation_id=conversation.id,
        platform_msg_id=platform_msg_id,
        direction='in',
        msg_type='text',
        content=message_content,
        sender_type='user'
    )
    db.add(message)
    
    # 更新对话
    conversation.last_message_at = datetime.utcnow()
    conversation.last_message_preview = message_content[:200] if len(message_content) > 200 else message_content
    conversation.unread_count += 1
    
    await db.commit()
    
    # TODO: 触发AI回复或转人工判断
    
    return {"conversation_id": str(conversation.id), "message_id": str(message.id)}


# ============ 平台订单查询 ============

@router.get("/orders/{platform_type}/{order_id}")
async def get_order(
    platform_type: str,
    order_id: str,
    shop_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """查询平台订单信息"""
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
            raise HTTPException(status_code=403, detail="无权访问")
    
    # TODO: 调用平台API查询订单
    # 这里返回模拟数据
    return {
        "order_id": order_id,
        "platform_type": platform_type,
        "status": "已发货",
        "buyer_nick": "买家昵称",
        "total_amount": 199.99,
        "items": [
            {
                "title": "商品名称",
                "sku": "规格信息",
                "quantity": 1,
                "price": 199.99
            }
        ],
        "logistics": {
            "company": "顺丰速运",
            "tracking_no": "SF1234567890"
        }
    }


# ============ 发送消息到平台 ============

async def send_platform_message(
    platform: Platform,
    platform_user_id: str,
    content: str,
    msg_type: str = 'text'
) -> bool:
    """发送消息到电商平台"""
    try:
        if platform.platform_type == 'taobao':
            # TODO: 调用淘宝API发送消息
            pass
        elif platform.platform_type == 'jd':
            # TODO: 调用京东API发送消息
            pass
        elif platform.platform_type == 'pdd':
            # TODO: 调用拼多多API发送消息
            pass
        
        # 模拟发送成功
        return True
    except Exception as e:
        return False
