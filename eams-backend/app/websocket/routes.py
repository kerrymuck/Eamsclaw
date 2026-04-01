"""
WebSocket路由
处理WebSocket连接和消息
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Optional
import json
import logging

from app.database import get_db
from app.auth import get_current_user_ws
from app.websocket.manager import get_connection_manager, manager
from app.services.ai import get_ai_engine

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    WebSocket聊天连接
    
    连接参数:
    - token: JWT认证令牌
    
    消息格式:
    {
        "type": "message",      // 消息类型
        "data": {...}           // 消息数据
    }
    """
    # 认证用户
    if not token:
        await websocket.close(code=4001, reason="缺少认证令牌")
        return
    
    try:
        user = get_current_user_ws(token, db)
    except Exception as e:
        await websocket.close(code=4002, reason="认证失败")
        return
    
    user_id = str(user.id)
    shop_id = str(user.shop_id) if hasattr(user, 'shop_id') else None
    
    if not shop_id:
        await websocket.close(code=4003, reason="用户未关联店铺")
        return
    
    # 建立连接
    await manager.connect(websocket, user_id, shop_id)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "data": {"message": "无效的JSON格式"}
                }, websocket)
                continue
            
            # 处理消息
            await handle_client_message(websocket, user_id, shop_id, message, db)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id, shop_id)
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        manager.disconnect(websocket, user_id, shop_id)


async def handle_client_message(
    websocket: WebSocket,
    user_id: str,
    shop_id: str,
    message: dict,
    db: Session
):
    """处理客户端消息"""
    msg_type = message.get("type")
    msg_data = message.get("data", {})
    
    if msg_type == "ping":
        # 心跳检测
        await manager.send_personal_message({
            "type": "pong",
            "data": {"timestamp": msg_data.get("timestamp")}
        }, websocket)
    
    elif msg_type == "subscribe_conversation":
        # 订阅会话消息
        conversation_id = msg_data.get("conversation_id")
        # TODO: 将会话ID与用户关联，用于后续消息推送
        await manager.send_personal_message({
            "type": "subscribed",
            "data": {"conversation_id": conversation_id}
        }, websocket)
    
    elif msg_type == "unsubscribe_conversation":
        # 取消订阅会话
        conversation_id = msg_data.get("conversation_id")
        await manager.send_personal_message({
            "type": "unsubscribed",
            "data": {"conversation_id": conversation_id}
        }, websocket)
    
    elif msg_type == "typing":
        # 正在输入状态
        conversation_id = msg_data.get("conversation_id")
        is_typing = msg_data.get("is_typing", False)
        # TODO: 广播给会话中的客户
        
    elif msg_type == "send_message":
        # 发送消息
        await handle_send_message(websocket, user_id, shop_id, msg_data, db)
    
    elif msg_type == "ai_reply":
        # 请求AI回复
        await handle_ai_reply(websocket, user_id, shop_id, msg_data, db)
    
    else:
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": f"未知消息类型: {msg_type}"}
        }, websocket)


async def handle_send_message(
    websocket: WebSocket,
    user_id: str,
    shop_id: str,
    data: dict,
    db: Session
):
    """处理发送消息"""
    conversation_id = data.get("conversation_id")
    content = data.get("content")
    message_type = data.get("message_type", "text")
    
    if not conversation_id or not content:
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": "缺少必要参数"}
        }, websocket)
        return
    
    # TODO: 保存消息到数据库
    # TODO: 发送到平台适配器
    
    # 确认消息已发送
    await manager.send_personal_message({
        "type": "message_sent",
        "data": {
            "conversation_id": conversation_id,
            "content": content,
            "timestamp": "..."
        }
    }, websocket)


async def handle_ai_reply(
    websocket: WebSocket,
    user_id: str,
    shop_id: str,
    data: dict,
    db: Session
):
    """处理AI回复请求"""
    conversation_id = data.get("conversation_id")
    customer_message = data.get("message")
    platform = data.get("platform")
    customer_id = data.get("customer_id")
    
    if not all([conversation_id, customer_message, platform, customer_id]):
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": "缺少必要参数"}
        }, websocket)
        return
    
    # 获取AI引擎
    ai_engine = get_ai_engine()
    
    # 生成AI回复
    try:
        response = await ai_engine.generate_reply(
            message=customer_message,
            customer_id=customer_id,
            platform=platform,
            shop_id=shop_id
        )
        
        # 发送AI回复建议
        await manager.send_personal_message({
            "type": "ai_suggestion",
            "data": {
                "conversation_id": conversation_id,
                "suggestion": response.content,
                "intent": response.intent.value,
                "confidence": response.confidence,
                "suggested_actions": response.suggested_actions,
                "need_human_review": response.need_human_review
            }
        }, websocket)
        
    except Exception as e:
        logger.error(f"AI回复生成失败: {e}")
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": "AI回复生成失败"}
        }, websocket)


# ============ 注册消息处理器 ============

def register_message_handlers():
    """注册WebSocket消息处理器"""
    
    async def handle_ping(websocket: WebSocket, user_id: str, message: dict):
        """处理心跳"""
        await manager.send_personal_message({
            "type": "pong",
            "data": {"timestamp": message.get("data", {}).get("timestamp")}
        }, websocket)
    
    manager.register_handler("ping", handle_ping)


# 启动时注册处理器
register_message_handlers()
