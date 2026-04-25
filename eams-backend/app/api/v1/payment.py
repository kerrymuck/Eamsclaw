"""
支付回调API - 支付宝/微信支付回调处理
"""

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from typing import Dict

from app.api.deps import get_db
from app.services.ai_power.payment import PaymentService

router = APIRouter()


@router.post("/payment/alipay/notify")
async def alipay_notify(
    request: Request,
    db: Session = Depends(get_db)
):
    """支付宝支付回调"""
    from app.services.payment.alipay import get_alipay_service
    
    # 获取回调数据
    data = await request.form()
    notify_data = dict(data)
    
    # 验证签名
    alipay = get_alipay_service()
    if alipay.is_configured():
        if not alipay.verify_notify(notify_data.copy()):
            logger.error("支付宝回调签名验证失败")
            return "fail"
    
    payment = PaymentService()
    payment.db = db
    
    success = await payment.handle_payment_notify('alipay', notify_data)
    
    # 支付宝要求返回 success
    return "success" if success else "fail"


@router.post("/payment/wechat/notify")
async def wechat_notify(
    request: Request,
    db: Session = Depends(get_db)
):
    """微信支付回调"""
    from app.services.payment.wechat import get_wechat_service
    from fastapi.responses import Response
    
    # 获取回调数据（XML格式）
    body = await request.body()
    
    # 验证签名
    wechat = get_wechat_service()
    if wechat.is_configured():
        verify_result = wechat.verify_notify(body)
        if not verify_result.get("verified"):
            logger.error("微信支付回调签名验证失败")
            return Response(
                content="<xml><return_code><![CDATA[FAIL]]></return_code></xml>",
                media_type="application/xml"
            )
        notify_data = verify_result.get("data", {})
    else:
        # 未配置时直接解析
        import xml.etree.ElementTree as ET
        root = ET.fromstring(body)
        notify_data = {child.tag: child.text for child in root}
    
    payment = PaymentService()
    payment.db = db
    
    success = await payment.handle_payment_notify('wechat', notify_data)
    
    # 微信要求返回XML
    if success:
        return Response(
            content="<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>",
            media_type="application/xml"
        )
    else:
        return Response(
            content="<xml><return_code><![CDATA[FAIL]]></return_code></xml>",
            media_type="application/xml"
        )


@router.get("/payment/alipay/mock")
async def alipay_mock(
    order_no: str,
    db: Session = Depends(get_db)
):
    """
    支付宝模拟支付（测试用）
    
    显示模拟支付页面，用户点击确认后才完成支付
    """
    from fastapi.responses import HTMLResponse
    
    # 先显示支付确认页面
    html = """
    <html>
    <head>
        <title>支付宝模拟支付</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f5f5f5;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }
            .payment-box {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 400px;
                width: 90%;
            }
            .logo {
                font-size: 48px;
                margin-bottom: 20px;
            }
            .title {
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 10px;
                color: #333;
            }
            .order-no {
                color: #666;
                font-size: 14px;
                margin-bottom: 30px;
            }
            .amount {
                font-size: 36px;
                font-weight: bold;
                color: #1677ff;
                margin-bottom: 30px;
            }
            .btn-pay {
                background: #1677ff;
                color: white;
                border: none;
                padding: 15px 60px;
                font-size: 18px;
                border-radius: 8px;
                cursor: pointer;
                width: 100%;
            }
            .btn-pay:hover {
                background: #4096ff;
            }
            .btn-cancel {
                background: #f5f5f5;
                color: #666;
                border: none;
                padding: 12px 40px;
                font-size: 16px;
                border-radius: 8px;
                cursor: pointer;
                width: 100%;
                margin-top: 10px;
            }
            .success { color: #52c41a; }
            .error { color: #ff4d4f; }
        </style>
    </head>
    <body>
        <div class="payment-box" id="paymentBox">
            <div class="logo">🔵</div>
            <div class="title">支付宝模拟支付</div>
            <div class="order-no">订单号：{}</div>
            <div class="amount" id="amount">加载中...</div>
            <button class="btn-pay" onclick="confirmPay()">确认支付</button>
            <button class="btn-cancel" onclick="cancelPay()">取消支付</button>
        </div>
        
        <script>
            // 获取订单金额
            async function loadOrderInfo() {{
                try {{
                    const res = await fetch('/api/v1/ai/recharge-orders?order_no={}');
                    const data = await res.json();
                    if (data.items && data.items[0]) {{
                        document.getElementById('amount').textContent = '¥' + data.items[0].amount.toFixed(2);
                    }}
                }} catch (e) {{
                    document.getElementById('amount').textContent = '¥--';
                }}
            }}
            
            async function confirmPay() {{
                const btn = document.querySelector('.btn-pay');
                btn.textContent = '支付中...';
                btn.disabled = true;
                
                // 调用支付确认接口
                const res = await fetch('/payment/alipay/mock/confirm?order_no={}', {{ method: 'POST' }});
                const result = await res.json();
                
                if (result.success) {{
                    document.getElementById('paymentBox').innerHTML = `
                        <div class="logo success">✅</div>
                        <div class="title success">支付成功</div>
                        <div class="order-no">订单号：{}</div>
                        <p>请关闭此页面返回应用</p>
                    `;
                    setTimeout(() => window.close(), 3000);
                }} else {{
                    document.getElementById('paymentBox').innerHTML = `
                        <div class="logo error">❌</div>
                        <div class="title error">支付失败</div>
                        <div class="order-no">${{result.error || '请重试'}}</div>
                        <button class="btn-pay" onclick="location.reload()">重新支付</button>
                    `;
                }}
            }}
            
            function cancelPay() {{
                window.close();
            }}
            
            loadOrderInfo();
        </script>
    </body>
    </html>
    """.format(order_no, order_no, order_no, order_no)
    
    return HTMLResponse(content=html)


@router.post("/payment/alipay/mock/confirm")
async def alipay_mock_confirm(
    order_no: str,
    db: Session = Depends(get_db)
):
    """模拟支付确认（用户点击支付按钮后调用）"""
    from fastapi.responses import JSONResponse
    
    notify_data = {
        "out_trade_no": order_no,
        "trade_no": f"MOCK{order_no}",
        "trade_status": "TRADE_SUCCESS",
        "total_amount": "0.01"
    }
    
    payment = PaymentService()
    payment.db = db
    
    success = await payment.handle_payment_notify('alipay', notify_data)
    
    return JSONResponse(content={"success": success, "order_no": order_no})


@router.get("/payment/wechat/mock")
async def wechat_mock(
    order_no: str,
    db: Session = Depends(get_db)
):
    """
    微信支付模拟支付（测试用）
    """
    # 模拟支付成功回调
    notify_data = {
        "out_trade_no": order_no,
        "transaction_id": f"MOCK{order_no}",
        "result_code": "SUCCESS",
        "total_fee": "1"
    }
    
    payment = PaymentService()
    payment.db = db
    
    success = await payment.handle_payment_notify('wechat', notify_data)
    
    from fastapi.responses import HTMLResponse
    
    html = """
    <html>
    <head><title>微信支付</title></head>
    <body style="text-align: center; padding: 50px;">
        <h1>微信支付模拟</h1>
        <p>订单号：{}</p>
        <p>{}</p>
        <script>setTimeout(() => window.close(), 3000);</script>
    </body>
    </html>
    """.format(order_no, "✅ 支付成功" if success else "❌ 支付失败")
    
    return HTMLResponse(content=html)
