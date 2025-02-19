# test_payment.py
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from httpx import AsyncClient
from app.models import Payment
from .base import BaseTester


class TestPayment(BaseTester):
    async def create_test_payments(self, count=10):
        """Helper method to create test payments."""
        for i in range(count):
            await Payment.create(
                document=f"DOC-{i}",
                beneficiary=f"Beneficiary {i}",
                amount=Decimal(f"{i}00.00"),
                date=datetime.now() - timedelta(days=i)
            )

    @pytest.fixture(autouse=True)
    async def cleanup_payments(self):
        """Automatically clean up payments after each test."""
        yield
        await self.cleanup()  # Clean up users and payments

    @pytest.mark.anyio
    async def test_get_payments_unauthenticated(self, client: AsyncClient):
        response = await client.get("/api/v1/pagamentos/")
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_get_payments_with_valid_token(self, client: AsyncClient):
        await self.create_test_user(client, cleanup=True)
        login_data = await self.create_test_login(client)
        headers = {"Authorization": f"Bearer {login_data['access_token']}"}
        
        await self.create_test_payments(3)
        response = await client.get("/api/v1/pagamentos/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        for payment in data:
            assert all(field in payment for field in ["date", "document", "beneficiary", "amount"])

    @pytest.mark.anyio
    async def test_pagination(self, client: AsyncClient):
        await self.create_test_user(client, cleanup=True)
        login_data = await self.create_test_login(client)
        headers = {"Authorization": f"Bearer {login_data['access_token']}"}
        
        await self.create_test_payments(10)
        response = await client.get("/api/v1/pagamentos/?skip=5&limit=3", headers=headers)
        
        assert response.status_code == 200
        assert len(response.json()) == 3

    @pytest.mark.anyio
    async def test_get_all_payments(self, client: AsyncClient):
        await self.create_test_user(client, cleanup=True)
        login_data = await self.create_test_login(client)
        headers = {"Authorization": f"Bearer {login_data['access_token']}"}
        
        await self.create_test_payments(15)
        response = await client.get("/api/v1/pagamentos/all", headers=headers)
        
        assert response.status_code == 200
        assert len(response.json()) == 15

    @pytest.mark.anyio
    async def test_date_filter(self, client: AsyncClient):
        await self.create_test_user(client, cleanup=True)
        login_data = await self.create_test_login(client)
        headers = {"Authorization": f"Bearer {login_data['access_token']}"}
        
        start_date = datetime.now() - timedelta(days=5)
        end_date = datetime.now() - timedelta(days=2)
        
        # Create payments within range
        for i in range(3):
            await Payment.create(
                document=f"DOC-FILTER-{i}",
                beneficiary="Test",
                amount=Decimal("100.00"),
                date=start_date + timedelta(days=i)
            )
        
        # Query with date filter
        response = await client.get(
            f"/api/v1/pagamentos/interval?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}",
            headers=headers
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 2

    @pytest.mark.anyio
    async def test_invalid_date_filter(self, client: AsyncClient):
        await self.create_test_user(client, cleanup=True)
        login_data = await self.create_test_login(client)
        headers = {"Authorization": f"Bearer {login_data['access_token']}"}
        
        # Invalid date format
        response = await client.get(
            "/api/v1/pagamentos/interval?start_date=invalid&end_date=2024-01-01",
            headers=headers
        )
        assert response.status_code == 500

    @pytest.mark.anyio
    async def test_api_key_auth(self, client: AsyncClient):
        # Generate API key
        await self.create_test_user(client, cleanup=True)
        login_data = await self.create_test_login(client)
        api_key = (await client.post(
            "/api/v1/apikeys/generate",
            headers={"Authorization": f"Bearer {login_data['access_token']}"}
        )).json()["api_key"]
        
        # Access with API key
        await self.create_test_payments(2)
        response = await client.get(
            "/api/v1/pagamentos/",
            headers={"X-API-KEY": api_key}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 2

    @pytest.mark.anyio
    async def test_rate_limits(self, client: AsyncClient):
        await self.create_test_user(client, cleanup=True)
        login_data = await self.create_test_login(client)
        headers = {"Authorization": f"Bearer {login_data['access_token']}"}
        
        # Exceed rate limit
        responses = []
        for _ in range(20):
            response = await client.get("/api/v1/pagamentos/", headers=headers)
            responses.append(response)
        response = await client.get("/api/v1/pagamentos/", headers=headers)
        rate_limited = any(resp.status_code == 429 for resp in responses)
        assert rate_limited, "Expected at least one request to be rate limited (429)"

    @pytest.mark.anyio
    async def test_disabled_user_access(self, client: AsyncClient):
        await self.create_test_user(client, cleanup=True)
        login_data = await self.create_test_login(client)
        headers = {"Authorization": f"Bearer {login_data['access_token']}"}
        
        # Disable user
        await client.put("/api/v1/users/disable", headers=headers)
        
        # Attempt to access payments
        response = await client.get("/api/v1/pagamentos/", headers=headers)
        assert response.status_code == 400
        assert "disabled" in response.json()["detail"]
