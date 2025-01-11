import pytest
from httpx import AsyncClient
from fastapi import FastAPI

pytestmark = pytest.mark.asyncio

@pytest.fixture
def user_data():
    """Test user data."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }

async def test_register_user(async_client: AsyncClient, user_data):
    """Test user registration."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json=user_data
    )
    assert response.status_code == 201, f"Registration failed: {response.json()}"
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]

async def test_login_user(async_client: AsyncClient, user_data):
    """Test user login."""
    # First register the user
    await async_client.post("/api/v1/auth/register", json=user_data)
    
    # Then try to login
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"],
        "grant_type": "password"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = await async_client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_login_wrong_password(async_client: AsyncClient, user_data):
    """Test login with wrong password."""
    # First register the user
    await async_client.post("/api/v1/auth/register", json=user_data)
    
    # Then try to login with wrong password
    login_data = {
        "username": user_data["email"],
        "password": "wrongpassword",
        "grant_type": "password"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = await async_client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers=headers
    )
    assert response.status_code == 401

async def test_register_duplicate_email(async_client: AsyncClient, user_data):
    """Test registering with an email that's already taken."""
    # Register first user
    await async_client.post("/api/v1/auth/register", json=user_data)
    
    # Try to register again with same email
    response = await async_client.post(
        "/api/v1/auth/register",
        json=user_data
    )
    assert response.status_code == 400 