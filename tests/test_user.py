""" Module for testing user endpoints.
    Make sure to that test_auth.py and test_apikeys.py pass before running
    these tests.
"""

import pytest
from httpx import AsyncClient
from .base import BaseTester


class TestUser(BaseTester):

    @pytest.mark.anyio
    async def test_protected_endpoint_disabled_user(self, client: AsyncClient):
        """
        Verify that a disabled user cannot access protected endpoints.
        """
        # Create a test user and login.
        await self.create_test_user(client, cleanup=True)
        login_response = await self.create_test_login(client)
        token = login_response["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Disable the user via the disable endpoint.
        disable_response = await client.put(
            "/api/v1/users/disable",
            headers=headers,
        )
        assert disable_response.status_code == 200
        login_response = await client.post(
            "/api/v1/auth/token",
            data=self.test_user,
        )
        assert login_response.status_code == 401

        # Now, attempt to access a protected endpoint.
        response = await client.post(
            "/api/v1/apikeys/generate",
            headers=headers,
        )
        assert response.status_code == 400
        assert response.json().get("detail") == "User account is disabled"
