from fastapi import APIRouter

from app.api.v1 import auth, merchants, packages, providers, ai_power, payment, settings, financial

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["认证"])
router.include_router(merchants.router, prefix="/merchants", tags=["商户管理"])
router.include_router(packages.router, prefix="/packages", tags=["套餐管理"])
router.include_router(providers.router, prefix="/providers", tags=["服务商管理"])
router.include_router(ai_power.router, prefix="/ai", tags=["AI算力中心"])
router.include_router(payment.router, prefix="/payment", tags=["支付系统"])
router.include_router(financial.router, prefix="/financial", tags=["财务管理"])
router.include_router(settings.router, prefix="/settings", tags=["系统设置"])
