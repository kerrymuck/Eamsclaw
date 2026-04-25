"""
电商平台Webhook接收服务
接收淘宝、京东、拼多多、抖音等平台的消息推送
"""

import logging
import json
import hmac
import hashlib
from typing import Dict, Optional
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.smart_customer_service import get_smart_customer_service

logger = logging.getLogger(__name__)

router = APIRouter()


class PlatformWebhookHandler:
    """平台Webhook处理器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.smart_service = get_smart_customer_service(db)
    
    async def handle_taobao_message(self, payload: Dict) -> Dict:
        """
        处理淘宝消息推送
        
        淘宝开放平台消息格式：
        {
            "buyer_nick": "买家昵称",
            "seller_nick": "卖家昵称",
            "tid": "订单ID",
            "content": "消息内容",
            "created": "消息时间",
            "item_id": "商品ID",
            "item_title": "商品标题",
            ...
        }
        """
        try:
            # 提取关键信息
            buyer_id = payload.get("buyer_nick")
            shop_id = await self._get_shop_by_platform_account("taobao", payload.get("seller_nick"))
            message_content = payload.get("content", "")
            item_id = payload.get("item_id")
            tid = payload.get("tid")
            
            # 获取商品信息
            product_info = None
            if item_id:
                product_info = await self._get_product_info(shop_id, item_id)
            
            # 获取订单信息
            order_info = None
            if tid:
                order_info = await self._get_order_info(shop_id, tid)
            
            # 调用智能客服处理
            result = await self.smart_service.handle_buyer_message(
                shop_id=shop_id,
                buyer_id=buyer_id,
                buyer_message=message_content,
                platform="taobao",
                product_info=product_info,
                order_info=order_info
            )
            
            # 如果成功，返回AI回复给淘宝
            if result["success"]:
                return {
                    "success": True,
                    "reply": result["reply"],
                    "auto_reply": True
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error"),
                    "auto_reply": False
                }
                
        except Exception as e:
            logger.error(f"处理淘宝消息失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def handle_jd_message(self, payload: Dict) -> Dict:
        """处理京东消息推送"""
        try:
            buyer_id = payload.get("pin")
            shop_id = await self._get_shop_by_platform_account("jd", payload.get("venderId"))
            message_content = payload.get("content", "")
            
            result = await self.smart_service.handle_buyer_message(
                shop_id=shop_id,
                buyer_id=buyer_id,
                buyer_message=message_content,
                platform="jd"
            )
            
            return {
                "success": result["success"],
                "reply": result.get("reply"),
                "auto_reply": result["success"]
            }
            
        except Exception as e:
            logger.error(f"处理京东消息失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def handle_pdd_message(self, payload: Dict) -> Dict:
        """处理拼多多消息推送"""
        try:
            buyer_id = payload.get("buyer_id")
            shop_id = await self._get_shop_by_platform_account("pdd", payload.get("mall_id"))
            message_content = payload.get("msg_content", "")
            
            result = await self.smart_service.handle_buyer_message(
                shop_id=shop_id,
                buyer_id=buyer_id,
                buyer_message=message_content,
                platform="pdd"
            )
            
            return {
                "success": result["success"],
                "reply": result.get("reply"),
                "auto_reply": result["success"]
            }
            
        except Exception as e:
            logger.error(f"处理拼多多消息失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def handle_douyin_message(self, payload: Dict) -> Dict:
        """处理抖音消息推送"""
        try:
            buyer_id = payload.get("user_id")
            shop_id = await self._get_shop_by_platform_account("douyin", payload.get("shop_id"))
            message_content = payload.get("text", "")
            
            result = await self.smart_service.handle_buyer_message(
                shop_id=shop_id,
                buyer_id=buyer_id,
                buyer_message=message_content,
                platform="douyin"
            )
            
            return {
                "success": result["success"],
                "reply": result.get("reply"),
                "auto_reply": result["success"]
            }
            
        except Exception as e:
            logger.error(f"处理抖音消息失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _get_shop_by_platform_account(self, platform: str, account: str) -> str:
        """根据平台账号获取商户ID"""
        # TODO: 从数据库查询平台授权绑定关系
        # 临时返回测试商户ID
        return "test-shop-id"
    
    async def _get_product_info(self, shop_id: str, item_id: str) -> Optional[Dict]:
        """获取商品信息"""
        # TODO: 从商品库查询
        return None
    
    async def _get_order_info(self, shop_id: str, order_id: str) -> Optional[Dict]:
        """获取订单信息"""
        # TODO: 从订单库查询
        return None


# ============== Webhook路由 ==============

@router.post("/taobao")
async def taobao_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """淘宝开放平台Webhook"""
    try:
        # 验证签名
        body = await request.body()
        signature = request.headers.get("X-Taobao-Sign")
        
        # TODO: 验证签名
        
        payload = await request.json()
        logger.info(f"收到淘宝消息: {json.dumps(payload, ensure_ascii=False)}")
        
        # 异步处理消息
        handler = PlatformWebhookHandler(db)
        result = await handler.handle_taobao_message(payload)
        
        return result
        
    except Exception as e:
        logger.error(f"淘宝Webhook处理失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jd")
async def jd_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """京东开放平台Webhook"""
    try:
        payload = await request.json()
        logger.info(f"收到京东消息: {json.dumps(payload, ensure_ascii=False)}")
        
        handler = PlatformWebhookHandler(db)
        result = await handler.handle_jd_message(payload)
        
        return result
        
    except Exception as e:
        logger.error(f"京东Webhook处理失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pdd")
async def pdd_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """拼多多开放平台Webhook"""
    try:
        payload = await request.json()
        logger.info(f"收到拼多多消息: {json.dumps(payload, ensure_ascii=False)}")
        
        handler = PlatformWebhookHandler(db)
        result = await handler.handle_pdd_message(payload)
        
        return result
        
    except Exception as e:
        logger.error(f"拼多多Webhook处理失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/douyin")
async def douyin_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """抖音开放平台Webhook"""
    try:
        payload = await request.json()
        logger.info(f"收到抖音消息: {json.dumps(payload, ensure_ascii=False)}")
        
        handler = PlatformWebhookHandler(db)
        result = await handler.handle_douyin_message(payload)
        
        return result
        
    except Exception as e:
        logger.error(f"抖音Webhook处理失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """测试Webhook - 模拟买家咨询"""
    try:
        payload = await request.json()
        
        shop_id = payload.get("shop_id", "test-shop-id")
        buyer_id = payload.get("buyer_id", "test-buyer")
        message = payload.get("message", "你好")
        platform = payload.get("platform", "test")
        
        handler = PlatformWebhookHandler(db)
        
        result = await handler.smart_service.handle_buyer_message(
            shop_id=shop_id,
            buyer_id=buyer_id,
            buyer_message=message,
            platform=platform
        )
        
        return result
        
    except Exception as e:
        logger.error(f"测试Webhook失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
