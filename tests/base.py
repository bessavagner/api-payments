import pytest
from async_asgi_testclient import TestClient

from app.models import User, Payment, ApiKey


class BaseTester:

    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123",
    }

    test_users = [
        {
            "username": f"testuser{idx}",
            "email": f"test{idx}@example.com",
            "password": f"{idx}securepassword123",
        }
        for idx in range(10)
    ]

    async def cleanup(self):
        await User.all().delete()
        await Payment.all().delete()
        await ApiKey.all().delete()

    async def setup(self):
        await self.cleanup()

    async def create_test_user(
        self,
        client: TestClient,
        test_user: User | dict = None,
        cleanup: bool = False,
    ) -> User:

        if cleanup:
            await self.cleanup()

        if test_user is None:
            test_user = self.test_user

        if cleanup:
            response = await client.post("/api/v1/auth/register", json=test_user)
            assert response.status_code == 201
        return await User.get(username=test_user["username"])

    async def create_test_login(self, client: TestClient) -> dict:
        test_user = {"username": "testuser", "password": "securepassword123"}
        response = await client.post("/api/v1/auth/token", data=test_user)
        assert response.status_code == 200
        return response.json()
