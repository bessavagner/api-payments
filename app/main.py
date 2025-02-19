import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from tortoise import Tortoise

from slowapi.errors import RateLimitExceeded

from app.config import settings, TORTOISE_ORM
from app.dependencies import limiter
from app.api.endpoints import auth, payments, users, apikeys
from app.logging_config import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        logger.info("Tortoise-ORM connected to database")
        yield
    except Exception as err:
        logger.error("Error connecting to database: %s", err)
    finally:
        await Tortoise.close_connections()
        logger.info("Tortoise-ORM connections closed")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth.router,
    prefix=f"{settings.API_PREFIX}{settings.API_VERSION}/auth",
    tags=["auth"],
)
app.include_router(
    payments.router,
    prefix=f"{settings.API_PREFIX}{settings.API_VERSION}/pagamentos",
    tags=["pagamentos"],
)
app.include_router(
    users.router,
    prefix=f"{settings.API_PREFIX}{settings.API_VERSION}/users",
    tags=["users"],
)
app.include_router(
    apikeys.router,
    prefix=f"{settings.API_PREFIX}{settings.API_VERSION}/apikeys",
    tags=["apikeys"],
)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}
