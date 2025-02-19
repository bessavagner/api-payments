""" Module for testing user endpoints.
    Make sure to that test_auth.py passes before running these tests.
"""

from datetime import timedelta

import pytest

from httpx import AsyncClient

from app.core.auth import create_access_token

from .base import BaseTester


class TestUser(BaseTester):

    @pytest.mark.anyio
    async def test_protected_endpoint_with_valid_token(
        self,
        client: AsyncClient,
    ):
        """
        Ensure that a valid access token allows access to a protected endpoint.
        Here, we use the API key generation endpoint as an example.
        """
        await self.create_test_user(client, cleanup=True)
        login_response = await self.create_test_login(client)
        token = login_response["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "/api/v1/apikeys/generate",
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert "api_key" in data

    @pytest.mark.anyio
    async def test_protected_endpoint_with_expired_token(
        self,
        client: AsyncClient,
    ):
        """
        Ensure that an expired access token is rejected when accessing
        protected endpoints.
        """
        await self.create_test_user(client, cleanup=True)
        await self.create_test_login(client)
        # Manually create an expired token (expiration set in the past).
        expired_token = create_access_token(
            {"sub": self.test_user["username"]},
            expires_delta=timedelta(seconds=-1),
        )
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await client.post(
            "/api/v1/apikeys/generate",
            headers=headers,
        )
        assert response.status_code == 401
        assert response.json().get("detail") == (
            "Invalid authentication credentials"
        )
