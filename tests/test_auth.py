import asyncio

import pytest
import bcrypt

from httpx import AsyncClient
from async_asgi_testclient import TestClient

from tortoise.exceptions import DoesNotExist

from app.models import User

from .base import BaseTester


class TestAuth(BaseTester):
    @pytest.mark.anyio
    async def test_user_registration(self, client: AsyncClient):
        user = await self.create_test_user(client, cleanup=True)
        assert user is not None
        assert bcrypt.checkpw(
            "securepassword123".encode(), user.hashed_password.encode()
        )

    @pytest.mark.anyio
    async def test_user_login(self, client: AsyncClient):
        response = await self.create_test_login(client)
        assert response["access_token"] is not None
        assert response["token_type"] == "bearer"

    @pytest.mark.anyio
    async def test_registration_existing_username(self, client: AsyncClient):
        # Create the initial user.
        await self.create_test_user(client)
        duplicate_username = {
            "username": "testuser",  # same username
            "email": "different@example.com",
            "password": "anotherpassword",
        }
        response = await client.post(
            "/api/v1/auth/register",
            json=duplicate_username,
        )
        assert response.status_code == 400
        json_resp = response.json()
        assert json_resp.get("detail") == "Username already registered"

    @pytest.mark.anyio
    async def test_registration_existing_email(self, client: AsyncClient):

        duplicate_email = self.test_user.copy()
        duplicate_email["username"] = "anotheruser"

        # Assert that the user does not exist.
        with pytest.raises(DoesNotExist):
            await self.create_test_user(client, duplicate_email)

        # Assert 400 response when trying to register with duplicate email.
        response = await client.post(
            "/api/v1/auth/register",
            json=duplicate_email,
        )
        assert response.status_code == 400

        # Assert that the response contains the expected error message.
        json_resp = response.json()
        assert json_resp.get("detail") == "Email already registered"

    @pytest.mark.anyio
    async def test_login_incorrect_password(self, client: AsyncClient):

        wrong_password_data = {
            "username": "testuser",
            "password": "wrongpassword",
        }
        response = await client.post(
            "/api/v1/auth/token",
            data=wrong_password_data,
        )
        assert response.status_code == 401
        json_resp = response.json()
        assert json_resp.get("detail") == "Incorrect username or password"

    @pytest.mark.anyio
    async def test_login_incorrect_username(self, client: AsyncClient):

        wrong_username_data = {
            "username": "nonexistentuser",
            "password": "any_password",
        }
        response = await client.post(
            "/api/v1/auth/token",
            data=wrong_username_data,
        )
        assert response.status_code == 401
        json_resp = response.json()
        assert json_resp.get("detail") == "Incorrect username or password"

    @pytest.mark.anyio
    async def test_registration_missing_fields(self, client: AsyncClient):
        """
        Test that registration fails with missing required fields.
        """
        # Missing email
        incomplete_data = {
            "username": "newuser",
            "password": "newpassword",
        }
        response = await client.post(
            "/api/v1/auth/register",
            json=incomplete_data,
        )
        assert response.status_code == 422

        # Missing password
        incomplete_data = {
            "username": "newuser",
            "email": "newuser@example.com",
        }
        response = await client.post(
            "/api/v1/auth/register",
            json=incomplete_data,
        )
        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_login_missing_fields(self, client: AsyncClient):
        """
        Test that login fails when required fields are missing.
        """
        # Missing password
        login_data = {"username": "testuser"}
        response = await client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 422

        # Missing username
        login_data = {"password": "securepassword123"}
        response = await client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_rate_limiting(self, client: AsyncClient):
        """
        Test that the rate limiting mechanism is active by sending several
        rapid requests. Here, we use the /health endpoint which is not
        authenticated.
        """
        responses = []

        for test_user in self.test_users:
            response = await client.post(
                "/api/v1/auth/register",
                json=test_user,
            )
            responses.append(response)
        # Check that at least one response returns 429 (Too Many Requests)
        rate_limited = any(resp.status_code == 429 for resp in responses)
        assert rate_limited, "Expected at least one request to be rate limited (429)"
        # Optionally, verify the rate limit error message.
        for resp in responses:
            if resp.status_code == 429:
                assert resp.json().get("detail") == "Too many requests"

        await self.cleanup()
