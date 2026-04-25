# API路由初始化
from . import (
    auth, dialog, knowledge, platform, analytics, upload, settings,
    ai_power, ai_power_admin, ai_power_provider, payment, system_settings,
    admin_provider, admin_finance, admin_merchant,
    provider_merchant, provider_license, provider_finance,
    webhook, conversation
)

__all__ = [
    "auth", "dialog", "knowledge", "platform", "analytics", "upload", "settings",
    "ai_power", "ai_power_admin", "ai_power_provider", "payment", "system_settings",
    "admin_provider", "admin_finance", "admin_merchant",
    "provider_merchant", "provider_license", "provider_finance",
    "webhook", "conversation"
]
