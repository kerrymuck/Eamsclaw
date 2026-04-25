import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()

# 创建Redis连接池
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True
)

# 创建Redis客户端
redis_client = redis.Redis(connection_pool=redis_pool)


async def get_redis():
    """获取Redis客户端"""
    return redis_client


async def set_cache(key: str, value: str, expire: int = 3600):
    """设置缓存"""
    await redis_client.set(key, value, ex=expire)


async def get_cache(key: str) -> str:
    """获取缓存"""
    return await redis_client.get(key)


async def delete_cache(key: str):
    """删除缓存"""
    await redis_client.delete(key)


async def close_redis():
    """关闭Redis连接"""
    await redis_pool.disconnect()
