"""
平台适配器模块初始化
动态加载所有适配器
"""

from .base import PlatformAdapter, UnifiedMessage, UnifiedOrder, MessageType, SenderType
from .registry import PlatformAdapterRegistry, PlatformMeta, load_adapters

# 导入具体适配器（会自动注册）
from . import taobao
from . import jd
from . import pdd
from . import douyin
from . import amazon

# 动态加载所有适配器
load_adapters()

__all__ = [
    'PlatformAdapter',
    'UnifiedMessage',
    'UnifiedOrder',
    'MessageType',
    'SenderType',
    'PlatformAdapterRegistry',
    'PlatformMeta',
    'load_adapters',
]
