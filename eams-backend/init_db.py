#!/usr/bin/env python3
"""
数据库初始化脚本
开发环境使用SQLite，自动创建表结构
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine
from app.models.user import Base

# 使用开发环境数据库URL
DATABASE_URL = "sqlite+aiosqlite:///./eams_dev.db"


async def init_database():
    """初始化数据库"""
    print("=" * 60)
    print("EAMS 数据库初始化")
    print("=" * 60)
    print(f"数据库: {DATABASE_URL}")
    print()
    
    # 创建引擎
    engine = create_async_engine(
        DATABASE_URL,
        echo=True
    )
    
    # 创建所有表
    print("正在创建数据表...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print()
    print("=" * 60)
    print("✅ 数据库初始化完成！")
    print("=" * 60)
    
    # 显示创建的表
    tables = list(Base.metadata.tables.keys())
    print(f"\n已创建 {len(tables)} 张表:")
    for i, table in enumerate(tables, 1):
        print(f"  {i:2d}. {table}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
