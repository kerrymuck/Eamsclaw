"""
AI算力系统测试脚本
测试AI调用、计费、充值流程
"""

import asyncio
import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
# 需要先登录获取token
AUTH_TOKEN = "your_auth_token_here"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}


def test_get_account():
    """测试获取账户信息"""
    print("\n=== 测试获取账户信息 ===")
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/ai/account", headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_get_models():
    """测试获取模型列表"""
    print("\n=== 测试获取模型列表 ===")
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/ai/models", headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_create_recharge():
    """测试创建充值订单"""
    print("\n=== 测试创建充值订单 ===")
    try:
        data = {
            "amount": 100,
            "payment_method": "alipay"
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/ai/recharge",
            headers=headers,
            json=data
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_mock_payment(order_no: str):
    """测试模拟支付"""
    print(f"\n=== 测试模拟支付 (订单: {order_no}) ===")
    try:
        # 打开模拟支付页面
        payment_url = f"{BASE_URL}/payment/alipay/mock?order_no={order_no}"
        print(f"Payment URL: {payment_url}")
        print("请在浏览器中打开此URL完成支付")
        return payment_url
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_chat():
    """测试AI聊天（带计费）"""
    print("\n=== 测试AI聊天（带计费） ===")
    try:
        data = {
            "model": "Kimi K2.5",
            "messages": [
                {"role": "user", "content": "你好，请介绍一下自己"}
            ],
            "temperature": 0.7
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/ai/chat",
            headers=headers,
            json=data
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_get_usage():
    """测试获取用量统计"""
    print("\n=== 测试获取用量统计 ===")
    try:
        resp = requests.get(
            f"{BASE_URL}/api/v1/ai/usage?days=7",
            headers=headers
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_get_transactions():
    """测试获取交易记录"""
    print("\n=== 测试获取交易记录 ===")
    try:
        resp = requests.get(
            f"{BASE_URL}/api/v1/ai/transactions",
            headers=headers
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return None


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("EAMS AI算力系统测试")
    print("=" * 50)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    
    # 1. 获取账户信息
    account = test_get_account()
    
    # 2. 获取模型列表
    models = test_get_models()
    
    # 3. 创建充值订单
    recharge = test_create_recharge()
    if recharge and recharge.get("order_no"):
        # 4. 模拟支付
        test_mock_payment(recharge["order_no"])
    
    # 5. AI聊天测试（需要有余额）
    # chat_result = test_chat()
    
    # 6. 获取用量统计
    usage = test_get_usage()
    
    # 7. 获取交易记录
    transactions = test_get_transactions()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    print("请确保:")
    print("1. 后端服务已启动 (python start.py)")
    print("2. 已配置 Moonshot API Key")
    print("3. 已登录并获取 AUTH_TOKEN")
    print("")
    
    # 更新token
    token = input("请输入登录后的JWT Token (或按Enter跳过): ").strip()
    if token:
        AUTH_TOKEN = token
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    
    run_all_tests()
