#!/usr/bin/env python3
"""
数据库验证脚本
检查模型定义和迁移脚本的一致性
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.user import Base
from app.models.conversation import Conversation, Message, Handoff
from app.models.knowledge import Knowledge, KnowledgeCategory
from app.models.stats import DailyStats, HourlyStats, IntentStats
from app.models.ai import IntentLog, ModelConfig
from app.models.system import Setting, AuditLog
from app.models.platform_config import PlatformConfig, ShopPlatformAuth, PlatformWebhookLog


def check_models():
    """检查所有模型是否正确加载"""
    print("=" * 60)
    print("数据库模型验证")
    print("=" * 60)
    
    models = [
        ("User", "用户表"),
        ("Shop", "店铺表"),
        ("ShopMember", "店铺成员表"),
        ("Platform", "平台绑定表"),
        ("Conversation", "对话表"),
        ("Message", "消息表"),
        ("Handoff", "转人工表"),
        ("KnowledgeCategory", "知识库分类表"),
        ("Knowledge", "知识库条目表"),
        ("DailyStats", "日统计表"),
        ("HourlyStats", "小时统计表"),
        ("IntentStats", "意图统计表"),
        ("IntentLog", "意图日志表"),
        ("ModelConfig", "模型配置表"),
        ("Setting", "系统设置表"),
        ("AuditLog", "审计日志表"),
        ("PlatformConfig", "平台配置表"),
        ("ShopPlatformAuth", "店铺平台授权表"),
        ("PlatformWebhookLog", "Webhook日志表"),
    ]
    
    all_passed = True
    
    for model_name, description in models:
        try:
            model_class = globals().get(model_name)
            if model_class:
                table_name = model_class.__tablename__
                columns = list(model_class.__table__.columns.keys())
                print(f"✅ {model_name:20s} | {description:15s} | 表名: {table_name:25s} | 字段数: {len(columns)}")
            else:
                print(f"❌ {model_name:20s} | {description:15s} | 模型未找到")
                all_passed = False
        except Exception as e:
            print(f"❌ {model_name:20s} | {description:15s} | 错误: {e}")
            all_passed = False
    
    print("=" * 60)
    
    # 检查表总数
    table_count = len(Base.metadata.tables)
    print(f"\n总表数: {table_count}")
    
    if table_count >= 17:
        print("✅ 表数量检查通过 (>= 17)")
    else:
        print(f"❌ 表数量不足: {table_count} < 17")
        all_passed = False
    
    return all_passed


def check_migration():
    """检查迁移脚本"""
    print("\n" + "=" * 60)
    print("迁移脚本验证")
    print("=" * 60)
    
    migration_file = "alembic/versions/001_initial.py"
    
    if not os.path.exists(migration_file):
        print(f"❌ 迁移脚本不存在: {migration_file}")
        return False
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键表
    tables = [
        'users', 'shops', 'shop_members', 'conversations', 'messages',
        'handoffs', 'knowledge_categories', 'knowledge', 'daily_stats',
        'hourly_stats', 'intent_stats', 'intent_logs', 'model_configs',
        'settings', 'audit_logs', 'platform_configs', 'shop_platform_auths',
        'platform_webhook_logs'
    ]
    
    all_passed = True
    for table in tables:
        if f"op.create_table('{table}'" in content:
            print(f"✅ 表 {table} 在迁移脚本中定义")
        else:
            print(f"❌ 表 {table} 在迁移脚本中未找到")
            all_passed = False
    
    # 检查索引
    indexes = [
        'ix_conversations_shop_id',
        'ix_conversations_status',
        'ix_messages_conversation_id',
        'ix_knowledge_shop_id',
    ]
    
    print("\n索引检查:")
    for index in indexes:
        if f"op.create_index('{index}'" in content:
            print(f"✅ 索引 {index}")
        else:
            print(f"⚠️ 索引 {index} 未找到 (可选)")
    
    return all_passed


def check_dependencies():
    """检查依赖"""
    print("\n" + "=" * 60)
    print("依赖检查")
    print("=" * 60)
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'alembic',
        'psycopg2-binary',
        'asyncpg',
        'redis',
        'pydantic',
        'pydantic-settings',
        'python-jose',
        'passlib',
        'python-multipart',
        'httpx',
        'websockets',
        'openai',
        'apscheduler',
    ]
    
    all_passed = True
    
    for package in required_packages:
        try:
            if package == 'psycopg2-binary':
                import psycopg2
                print(f"✅ {package:20s} 已安装")
            elif package == 'python-jose':
                import jose
                print(f"✅ {package:20s} 已安装")
            elif package == 'passlib':
                import passlib
                print(f"✅ {package:20s} 已安装")
            elif package == 'python-multipart':
                import multipart
                print(f"✅ {package:20s} 已安装")
            else:
                __import__(package.replace('-', '_'))
                print(f"✅ {package:20s} 已安装")
        except ImportError:
            print(f"❌ {package:20s} 未安装")
            all_passed = False
    
    return all_passed


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("EAMS 后端数据库验证")
    print("=" * 60 + "\n")
    
    results = []
    
    # 检查模型
    results.append(("模型定义", check_models()))
    
    # 检查迁移
    results.append(("迁移脚本", check_migration()))
    
    # 检查依赖
    results.append(("依赖包", check_dependencies()))
    
    # 汇总
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name:15s} | {status}")
    
    all_passed = all(passed for _, passed in results)
    
    print("=" * 60)
    if all_passed:
        print("✅ 所有验证通过！数据库配置正确。")
        return 0
    else:
        print("❌ 部分验证失败，请检查上述错误。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
