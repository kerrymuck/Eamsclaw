"""
WebSocket 实时通信模块
处理客户端WebSocket连接和消息推送
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import logging

from app.core.database import get_db
from app.services.message_processor import MessageProcessor

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 用户ID -> WebSocket连接集合
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # WebSocket -> 用户信息
        self.connection_info: Dict[WebSocket, dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, shop_id: str):
        """建立连接"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.connection_info[websocket] = {
            "user_id": user_id,
            "shop_id": shop_id
        }
        
        logger.info(f"WebSocket连接建立: user_id={user_id}, shop_id={shop_id}")
    
    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        info = self.connection_info.get(websocket)
        if info:
            user_id = info["user_id"]
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            del self.connection_info[websocket]
            logger.info(f"WebSocket连接断开: user_id={user_id}")
    
    async def send_to_user(self, user_id: str, message: dict):
        """发送消息给指定用户"""
        if user_id not in self.active_connections:
            return
        
        disconnected = []
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                disconnected.append(websocket)
        
        # 清理断开的连接
        for ws in disconnected:
            self.disconnect(ws)
    
    async def send_to_shop(self, shop_id: str, message: dict):
        """发送消息给店铺所有在线用户"""
        for websocket, info in self.connection_info.items():
            if info["shop_id"] == shop_id:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"发送消息失败: {e}")
    
    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        disconnected = []
        for websocket in list(self.connection_info.keys()):
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                disconnected.append(websocket)
        
        for ws in disconnected:
            self.disconnect(ws)
    
    def get_online_users(self, shop_id: str = None) -> list:
        """获取在线用户列表"""
        if shop_id:
            users = set()
            for info in self.connection_info.values():
                if info["shop_id"] == shop_id:
                    users.add(info["user_id"])
            return list(users)
        return list(self.active_connections.keys())


# 全局连接管理器实例
manager = ConnectionManager()


async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db = Depends(get_db)
):
    """
    WebSocket连接端点
    
    连接URL: ws://localhost:8000/ws/chat?token=xxx
    """
    # 验证token并获取用户信息
    from app.api.v1.auth import get_current_user
    
    try:
        user = await get_current_user(token, db)
    except Exception as e:
        logger.error(f"WebSocket认证失败: {e}")
        await websocket.close(code=4001, reason="认证失败")
        return
    
    # 建立连接
    await manager.connect(websocket, str(user.id), str(user.shop_id) if user.shop_id else None)
    
    # 发送连接成功消息
    await websocket.send_json({
        "type": "connected",
        "message": "WebSocket连接成功",
        "data": {
            "user_id": str(user.id),
            "username": user.username
        }
    })
    
    message_processor = MessageProcessor(db)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "ping":
                    # 心跳响应
                    await websocket.send_json({"type": "pong"})
                
                elif msg_type == "send_message":
                    # 发送消息
                    conversation_id = message.get("conversation_id")
                    content = message.get("content")
                    
                    result = await message_processor.send_manual_reply(
                        conversation_id=conversation_id,
                        content=content,
                        sender_id=str(user.id),
                        sender_name=user.username
                    )
                    
                    # 通知发送者
                    await websocket.send_json({
                        "type": "message_sent",
                        "data": result
                    })
                
                elif msg_type == "typing":
                    # 正在输入状态
                    conversation_id = message.get("conversation_id")
                    # 广播给会话参与者
                    await manager.send_to_shop(
                        str(user.shop_id),
                        {
                            "type": "agent_typing",
                            "conversation_id": conversation_id,
                            "agent_name": user.username
                        }
                    )
                
                elif msg_type == "mark_read":
                    # 标记已读
                    conversation_id = message.get("conversation_id")
                    await message_processor.mark_conversation_read(
                        conversation_id=conversation_id,
                        user_id=str(user.id)
                    )
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"未知的消息类型: {msg_type}"
                    })
            
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "无效的JSON格式"
                })
            except Exception as e:
                logger.error(f"处理WebSocket消息失败: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket异常: {e}")
        manager.disconnect(websocket)


async def notify_new_message(shop_id: str, conversation_id: str, message: dict):
    """通知店铺有新消息"""
    await manager.send_to_shop(shop_id, {
        "type": "new_message",
        "conversation_id": conversation_id,
        "message": message
    })


async def notify_conversation_update(shop_id: str, conversation_id: str, update_type: str, data: dict):
    """通知会话更新"""
    await manager.send_to_shop(shop_id, {
        "type": "conversation_update",
        "update_type": update_type,
        "conversation_id": conversation_id,
        "data": data
    })


async def notify_handoff_request(shop_id: str, conversation_id: str, handoff_info: dict):
    """通知转人工请求"""
    await manager.send_to_shop(shop_id, {
        "type": "handoff_request",
        "conversation_id": conversation_id,
        "handoff": handoff_info
    })
