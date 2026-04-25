"""
数据库类型兼容性处理
支持PostgreSQL和SQLite
"""

from sqlalchemy import String, TypeDecorator, JSON as SA_JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class UUID(TypeDecorator):
    """
    跨数据库兼容的UUID类型
    - PostgreSQL: 使用原生UUID类型
    - SQLite: 使用String(36)存储
    """
    impl = String(36)
    cache_ok = True
    
    def __init__(self, as_uuid=True):
        self.as_uuid = as_uuid
        super().__init__()
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=self.as_uuid))
        else:
            return dialect.type_descriptor(String(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == 'postgresql':
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


class INET(TypeDecorator):
    """
    跨数据库兼容的INET类型 (IP地址)
    - PostgreSQL: 使用原生INET类型
    - SQLite: 使用String(45)存储 (支持IPv6)
    """
    impl = String(45)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import INET as PG_INET
            return dialect.type_descriptor(PG_INET())
        else:
            return dialect.type_descriptor(String(45))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)
    
    def process_result_value(self, value, dialect):
        return value


class ARRAY(TypeDecorator):
    """
    跨数据库兼容的ARRAY类型
    - PostgreSQL: 使用原生ARRAY类型
    - SQLite: 使用JSON存储
    """
    impl = SA_JSON
    cache_ok = True
    
    def __init__(self, item_type=None, as_tuple=False, dimensions=None, zero_indexes=False):
        self.item_type = item_type
        self.as_tuple = as_tuple
        self.dimensions = dimensions
        self.zero_indexes = zero_indexes
        super().__init__()
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
            return dialect.type_descriptor(PG_ARRAY(self.item_type))
        else:
            return dialect.type_descriptor(SA_JSON())
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == 'postgresql':
            return value
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value


# JSON类型别名
JSON = SA_JSON
