import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import get_db, AsyncSessionLocal


# 测试客户端
@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# 数据库会话
@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


# 测试认证
async def get_auth_headers(client: AsyncClient, username: str = "admin", password: str = "admin"):
    response = await client.post("/api/v1/auth/login", json={
        "username": username,
        "password": password
    })
    data = response.json()
    token = data.get("data", {}).get("access_token")
    return {"Authorization": f"Bearer {token}"}


# ==================== 认证测试 ====================

@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """测试登录"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """测试错误密码"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "wrong"
    })
    assert response.status_code == 401


# ==================== 商户管理测试 ====================

@pytest.mark.asyncio
async def test_list_merchants(client: AsyncClient):
    """测试获取商户列表"""
    headers = await get_auth_headers(client)
    response = await client.get("/api/v1/merchants", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "items" in data["data"]


@pytest.mark.asyncio
async def test_create_merchant(client: AsyncClient):
    """测试创建商户"""
    headers = await get_auth_headers(client)
    response = await client.post("/api/v1/merchants", headers=headers, json={
        "name": "测试商户",
        "company_name": "测试公司",
        "contact_name": "张三",
        "contact_phone": "13800138000"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200


# ==================== AI算力测试 ====================

@pytest.mark.asyncio
async def test_list_ai_models(client: AsyncClient):
    """测试获取AI模型列表"""
    headers = await get_auth_headers(client)
    response = await client.get("/api/v1/ai/models", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_ai_chat(client: AsyncClient):
    """测试AI对话"""
    headers = await get_auth_headers(client)
    response = await client.post("/api/v1/ai/chat", headers=headers, json={
        "model": "moonshot/kimi-k2.5",
        "messages": [{"role": "user", "content": "你好"}],
        "temperature": 0.7
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "content" in data["data"]


# ==================== 支付测试 ====================

@pytest.mark.asyncio
async def test_create_recharge_order(client: AsyncClient):
    """测试创建充值订单"""
    headers = await get_auth_headers(client)
    response = await client.post("/api/v1/payment/recharge", headers=headers, json={
        "amount": 100.00,
        "payment_method": "wechat"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "order_no" in data["data"]


@pytest.mark.asyncio
async def test_list_recharge_orders(client: AsyncClient):
    """测试获取充值记录"""
    headers = await get_auth_headers(client)
    response = await client.get("/api/v1/payment/orders", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "items" in data["data"]


# ==================== 设置测试 ====================

@pytest.mark.asyncio
async def test_list_settings(client: AsyncClient):
    """测试获取设置列表"""
    headers = await get_auth_headers(client)
    response = await client.get("/api/v1/settings", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200


@pytest.mark.asyncio
async def test_update_setting(client: AsyncClient):
    """测试更新设置"""
    headers = await get_auth_headers(client)
    response = await client.put("/api/v1/settings/test_key", headers=headers, json={
        "value": "test_value"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200


# ==================== 健康检查 ====================

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """测试健康检查"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
