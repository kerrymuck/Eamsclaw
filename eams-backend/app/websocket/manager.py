"""
WebSocket管理器
支持实时消息推送
"""

from typing import Dict, Set, Optional, Callable, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket连接管理器
    管理客服端的WebSocket连接
    """
    
    def __init__(self):
        # 用户ID -> WebSocket连接集合
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
        # 店铺ID -> 在线客服用户ID集合
        self.shop_agents: Dict[str, Set[str]] = {}
        
        # 用户ID -> 当前处理的会话ID
        user_conversations: Dict[str, str] = {}
        
        # 消息处理器
        self.message_handlers: Dict[str, Callable] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, shop_id: str):
        """
        建立WebSocket连接
        
        Args:
            websocket: WebSocket连接
            user_id: 用户ID
            shop_id: 店铺ID
        """
        await websocket.accept()
        
        # 添加到用户连接集合
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # 添加到店铺客服集合
        if shop_id not in self.shop_agents:
            self.shop_agents[shop_id] = set()
        self.shop_agents[shop_id].add(user_id)
        
        logger.info(f"用户 {user_id} 连接到店铺 {shop_id}")
        
        # 发送连接成功消息
        await self.send_personal_message({
            "type": "connected",
            "data": {
                "user_id": user_id,
                "shop_id": shop_id,
                "timestamp": datetime.now().isoformat()
            }
        }, websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: str, shop_id: str):
        """断开WebSocket连接"""
        # 从用户连接集合移除
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # 从店铺客服集合移除
        if shop_id in self.shop_agents:
            self.shop_agents[shop_id].discard(user_id)
            if not self.shop_agents[shop_id]:
                del self.shop_agents[shop_id]
        
        logger.info(f"用户 {user_id} 断开连接")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送个人消息失败: {e}")
    
    async def send_to_user(self, user_id: str, message: dict):
        """发送消息给指定用户的所有连接"""
        if user_id not in self.active_connections:
            return
        
        disconnected = set()
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"发送消息给用户 {user_id} 失败: {e}")
                disconnected.add(websocket)
        
        # 清理断开的连接
        for websocket in disconnected:
            self.active_connections[user_id].discard(websocket)
    
    async def send_to_shop(self, shop_id: str, message: dict, exclude_user: str = None):
        """发送消息给店铺的所有在线客服"""
        if shop_id not in self.shop_agents:
            return
        
        for user_id in self.shop_agents[shop_id]:
            if user_id != exclude_user:
                await self.send_to_user(user_id, message)
    
    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        for user_id, connections in self.active_connections.items():
            disconnected = set()
            for websocket in connections:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"广播消息失败: {e}")
                    disconnected.add(websocket)
            
            # 清理断开的连接
            for websocket in disconnected:
                connections.discard(websocket)
    
    def is_user_online(self, user_id: str) -> bool:
        """检查用户是否在线"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    def get_shop_online_count(self, shop_id: str) -> int:
        """获取店铺在线客服数量"""
        return len(self.shop_agents.get(shop_id, set()))
    
    def get_online_users(self) -> list:
        """获取所有在线用户ID"""
        return list(self.active_connections.keys())
    
    def register_handler(self, message_type: str, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
    
    async def handle_message(self, websocket: WebSocket, user_id: str, message: dict):
        """处理收到的消息"""
        msg_type = message.get("type")
        
        if msg_type in self.message_handlers:
            try:
                await self.message_handlers[msg_type](websocket, user_id, message)
            except Exception as e:
                logger.error(f"处理消息失败: {e}")
                await self.send_personal_message({
                    "type": "error",
                    "data": {"message": "消息处理失败"}
                }, websocket)
        else:
            await self.send_personal_message({
                "type": "error",
                "data": {"message": f"未知消息类型: {msg_type}"}
            }, websocket)


# 全局连接管理器实例
manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """获取连接管理器实例"""
    return manager


# ============ 消息推送辅助函数 ============

async def notify_new_message(
    conversation_id: str,
    message: dict,
    shop_id: str,
    assigned_user_id: str = None
):
    """
    通知有新消息
    
    Args:
        conversation_id: 会话ID
        message: 消息内容
        shop_id: 店铺ID
        assigned_user_id: 分配的客服ID（如果有）
    """
    notification = {
        "type": "new_message",
        "data": {
            "conversation_id": conversation_id,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    if assigned_user_id:
        # 发送给分配的客服
        await manager.send_to_user(assigned_user_id, notification)
    else:
        # 发送给店铺所有客服
        await manager.send_to_shop(shop_id, notification)


async def notify_conversation_assigned(
    conversation_id: str,
    user_id: str,
    assigned_by: str = None
):
    """通知会话被分配"""
    notification = {
        "type": "conversation_assigned",
        "data": {
            "conversation_id": conversation_id,
            "assigned_to": user_id,
            "assigned_by": assigned_by,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    await manager.send_to_user(user_id, notification)


async def notify_conversation_closed(
    conversation_id: str,
    shop_id: str,
    closed_by: str
):
    """通知会话被关闭"""
    notification = {
        "type": "conversation_closed",
        "data": {
            "conversation_id": conversation_id,
            "closed_by": closed_by,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    await manager.send_to_shop(shop_id, notification)


async def notify_typing(
    conversation_id: str,
    user_id: str,
    is_typing: bool
):
    """通知正在输入状态"""
    notification = {
        "type": "typing",
        "data": {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "is_typing": is_typing,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # 发送给会话中的其他参与者
    # TODO: 实现会话参与者列表


async def notify_customer_online(
    customer_id: str,
    platform: str,
    shop_id: str,
    is_online: bool
):
    """通知客户上下线状态"""
    notification = {
        "type": "customer_status",
        "data": {
            "customer_id": customer_id,
            "platform": platform,
            "shop_id": shop_id,
            "is_online": is_online,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    await manager.send_to_shop(shop_id, notification)


async def notify_order_update(
    order_id: str,
    shop_id: str,
    update_type: str,
    update_data: dict
):
    """通知订单更新"""
    notification = {
        "type": "order_update",
        "data": {
            "order_id": order_id,
            "update_type": update_type,
            "update_data": update_data,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    await manager.send_to_shop(shop_id, notification)
