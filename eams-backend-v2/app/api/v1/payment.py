from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from pydantic import BaseModel
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.base import success_response
from app.middlewares.auth import require_merchant
from app.services.payment import recharge_service
from app.models.payment import PaymentMethod

router = APIRouter()


class RechargeRequest(BaseModel):
    amount: Decimal
    payment_method: str  # wechat, alipay


@router.post("/recharge")
async def create_recharge(
    request: RechargeRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_merchant)
):
    """创建充值订单"""
    # TODO: 从token获取商户ID
    merchant_id = 1
    
    payment_method = PaymentMethod.WECHAT if request.payment_method == "wechat" else PaymentMethod.ALIPAY
    
    order = await recharge_service.create_order(
        db,
        merchant_id=merchant_id,
        amount=request.amount,
        payment_method=payment_method
    )
    
    return success_response({
        "order_no": order.order_no,
        "amount": float(order.amount),
        "pay_url": f"/api/v1/payment/mock?order_no={order.order_no}&amount={order.amount}"
    })


@router.get("/orders")
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_merchant)
):
    """获取充值记录"""
    # TODO: 从token获取商户ID
    merchant_id = 1
    
    skip = (page - 1) * page_size
    orders = await recharge_service.get_merchant_orders(db, merchant_id, skip, page_size, status)
    
    return success_response({
        "total": len(orders),
        "page": page,
        "page_size": page_size,
        "pages": 1,
        "items": [o.to_dict() for o in orders]
    })


@router.get("/orders/{order_no}")
async def get_order(
    order_no: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_merchant)
):
    """获取订单详情"""
    order = await recharge_service.get_by_order_no(db, order_no)
    if not order:
        from app.exceptions import NotFoundError
        raise NotFoundError("订单不存在")
    return success_response(order.to_dict())


# 支付回调
@router.post("/webhook/wechat")
async def wechat_webhook(request: Request):
    """微信支付回调"""
    # TODO: 验证签名并处理回调
    return success_response(message="处理成功")


@router.post("/webhook/alipay")
async def alipay_webhook(request: Request):
    """支付宝回调"""
    # TODO: 验证签名并处理回调
    return success_response(message="处理成功")


# 模拟支付页面
@router.get("/mock")
async def mock_payment_page(
    order_no: str,
    amount: Decimal,
    db: AsyncSession = Depends(get_db)
):
    """模拟支付页面"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>支付确认</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
            .container {{ max-width: 400px; margin: 0 auto; border: 1px solid #ddd; padding: 30px; border-radius: 10px; }}
            .amount {{ font-size: 36px; color: #333; margin: 20px 0; font-weight: bold; }}
            .btn {{ 
                padding: 15px 40px; 
                margin: 10px; 
                font-size: 16px;
                cursor: pointer;
                border: none;
                border-radius: 5px;
            }}
            .btn-success {{ background: #07c160; color: white; }}
            .btn-cancel {{ background: #999; color: white; }}
            .order-info {{ color: #666; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>订单支付</h2>
            <div class="order-info">订单号: {order_no}</div>
            <div class="amount">¥{amount}</div>
            <button class="btn btn-success" onclick="confirmPay()">确认支付</button>
            <button class="btn btn-cancel" onclick="cancelPay()">取消</button>
        </div>
        <script>
            async function confirmPay() {{
                try {{
                    const response = await fetch('/api/v1/payment/mock/confirm?order_no={order_no}', {{method: 'POST'}});
                    const data = await response.json();
                    if (data.code === 200) {{
                        alert('支付成功！');
                    }} else {{
                        alert('支付失败: ' + data.message);
                    }}
                }} catch (e) {{
                    alert('支付成功！（模拟）');
                }}
                window.close();
            }}
            function cancelPay() {{
                alert('支付已取消');
                window.close();
            }}
        </script>
    </body>
    </html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html)


@router.post("/mock/confirm")
async def mock_payment_confirm(
    order_no: str,
    db: AsyncSession = Depends(get_db)
):
    """模拟支付确认"""
    order = await recharge_service.confirm_payment(db, order_no, payment_no=f"MOCK{order_no}")
    if order:
        return success_response(message="支付成功")
    return success_response(code=400, message="支付失败")
