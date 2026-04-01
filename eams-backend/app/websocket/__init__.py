"""
WebSocket模块初始化
"""

from .manager import (
    ConnectionManager,
    get_connection_manager,
    notify_new_message,
    notify_conversation_assigned,
    notify_conversation_closed,
    notify_typing,
    notify_customer_online,
    notify_order_update,
)

from .routes import router as websocket_router

__all__ = [
    'ConnectionManager',
    'get_connection_manager',
    'notify_new_message',
    'notify_conversation_assigned',
    'notify_conversation_closed',
    'notify_typing',
    'notify_customer_online',
    'notify_order_update',
    'websocket_router',
]
