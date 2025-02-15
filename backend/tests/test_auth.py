import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from ..app import app
import os

# 測試數據
test_user = {
    "name": "Test User",
    "email": "test@example.com",
    "password": "testpassword123"
}

@pytest.mark.asyncio
async def test_register():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/register", json=test_user)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == test_user["name"]
        assert data["email"] == test_user["email"]

@pytest.mark.asyncio
async def test_register_duplicate_email():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 先註冊一個用戶
        await ac.post("/api/v1/auth/register", json=test_user)
        # 嘗試使用相同的郵箱再次註冊
        response = await ac.post("/api/v1/auth/register", json=test_user)
        assert response.status_code == 400
        assert response.json()["message"] == "Email already registered"

@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 先註冊
        await ac.post("/api/v1/auth/register", json=test_user)
        
        # 登入
        login_data = {
            "username": test_user["email"],
            "password": test_user["password"]
        }
        response = await ac.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        login_data = {
            "username": test_user["email"],
            "password": "wrongpassword"
        }
        response = await ac.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
        assert response.json()["message"] == "Incorrect email or password"

@pytest.mark.asyncio
async def test_get_current_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 先登入獲取 token
        login_data = {
            "username": test_user["email"],
            "password": test_user["password"]
        }
        login_response = await ac.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # 使用 token 獲取當前用戶信息
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"] 