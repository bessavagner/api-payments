import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest

from tortoise.contrib.test import MEMORY_SQLITE

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.main import app

os.environ["DATABASE_URL"] = MEMORY_SQLITE
ClientManagerType = AsyncGenerator[AsyncClient, None]


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@asynccontextmanager
async def client_manager(
    app_,
    base_url="http://test",
    **kw,
) -> ClientManagerType:
    app.state.testing = True
    async with LifespanManager(app_):
        transport = ASGITransport(app=app_)
        async with AsyncClient(
            transport=transport,
            base_url=base_url,
            **kw,
        ) as c:
            yield c


@pytest.fixture(scope="module")
async def client() -> ClientManagerType:
    async with client_manager(app) as c:
        yield c
