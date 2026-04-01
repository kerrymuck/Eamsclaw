"""
平台适配器注册表
支持动态扩展
"""

from typing import Dict, Type, List
from .base import PlatformAdapter


class PlatformAdapterRegistry:
    """
    平台适配器注册表
    支持动态注册和获取平台适配器
    """
    
    _adapters: Dict[str, Type[PlatformAdapter]] = {}
    _platform_info: Dict[str, Dict] = {}
    
    @classmethod
    def register(cls, adapter_class: Type[PlatformAdapter]):
        """
        注册平台适配器
        
        Args:
            adapter_class: 适配器类
        """
        platform_id = adapter_class.platform_id
        if not platform_id:
            raise ValueError(f"适配器 {adapter_class.__name__} 必须设置 platform_id")
        
        cls._adapters[platform_id] = adapter_class
        cls._platform_info[platform_id] = {
            'id': platform_id,
            'name': adapter_class.platform_name,
            'type': adapter_class.platform_type,
            'category': adapter_class.platform_category,
        }
        print(f"✅ 注册平台适配器: {platform_id} ({adapter_class.platform_name})")
    
    @classmethod
    def get_adapter(cls, platform_id: str) -> PlatformAdapter:
        """
        获取平台适配器实例
        
        Args:
            platform_id: 平台ID
            
        Returns:
            适配器实例
            
        Raises:
            ValueError: 如果平台不支持
        """
        adapter_class = cls._adapters.get(platform_id)
        if not adapter_class:
            raise ValueError(f"未找到平台适配器: {platform_id}")
        return adapter_class()
    
    @classmethod
    def list_platforms(cls) -> List[Dict]:
        """
        列出所有支持的平台
        
        Returns:
            平台信息列表
        """
        return list(cls._platform_info.values())
    
    @classmethod
    def is_supported(cls, platform_id: str) -> bool:
        """
        检查平台是否支持
        
        Args:
            platform_id: 平台ID
            
        Returns:
            是否支持
        """
        return platform_id in cls._adapters
    
    @classmethod
    def get_adapter_count(cls) -> int:
        """
        获取已注册的适配器数量
        
        Returns:
            数量
        """
        return len(cls._adapters)


# 元类 - 自动注册平台适配器
class PlatformMeta(type):
    """
    元类 - 自动注册平台适配器
    使用此元类的适配器类会自动注册到注册表
    """
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        # 排除基类本身和抽象类
        if (name != 'PlatformAdapter' and 
            not namespace.get('_is_base', False) and
            hasattr(cls, 'platform_id') and 
            cls.platform_id):
            try:
                PlatformAdapterRegistry.register(cls)
            except Exception as e:
                print(f"⚠️ 注册适配器失败 {name}: {e}")
        return cls


def load_adapters():
    """
    动态加载所有平台适配器
    在应用启动时调用
    """
    import os
    import importlib
    from pathlib import Path
    
    current_dir = Path(__file__).parent
    
    # 遍历所有适配器文件
    for file in current_dir.glob("*.py"):
        if file.stem not in ["__init__", "base"]:
            try:
                # 动态导入模块，触发元类注册
                importlib.import_module(f"app.services.platform.{file.stem}")
            except Exception as e:
                print(f"⚠️ 加载适配器失败 {file.stem}: {e}")
    
    print(f"✅ 共加载 {PlatformAdapterRegistry.get_adapter_count()} 个平台适配器")
