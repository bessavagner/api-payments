import logging
from typing import Optional

import bcrypt

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from slowapi import Limiter
from slowapi.util import get_remote_address

from jwt import PyJWTError

from app.core.auth import verify_token
from app.models import User, ApiKey
from app.config import settings

logger = logging.getLogger("app.dependencies")
limiter = Limiter(
    key_func=get_remote_address,
    auto_check=True,
    enabled=True,
    default_limits=["5/second"],
)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}{settings.API_VERSION}/auth/token",
    auto_error=False,
)


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
):
   
    """
    Checks for an API key in the request headers or query parameters
    and returns the associated user if found. If no API key is found,
    it falls back to JWT token authentication and returns the user
    associated with the given token. If no token is provided, it raises
    a 401 error.
    
    :param request: The FastAPI request object
    :param token: The JWT token to verify
    :return: The associated user
    :raises HTTPException: If the API key is invalid, or if the user is disabled
    """
    logger.debug("Checking for API key...")
    api_key = request.headers.get("X-API-KEY") or request.query_params.get(
        "api_key",
    )
    if api_key:
        key_prefix = api_key[:10]
        logger.debug("API key provided: %s...", key_prefix)
        potential_keys = await ApiKey.filter(
            key_prefix=key_prefix,
        ).prefetch_related("user")
        for key in potential_keys:
            if bcrypt.checkpw(
                api_key.encode("utf-8"),
                key.hashed_key.encode("utf-8"),
            ):
                if key.user.disabled:
                    raise HTTPException(
                        status_code=400,
                        detail="User disabled",
                    )
                return key.user
        api_keys = await ApiKey.all().prefetch_related("user")
        logger.debug("Found %d API keys in the database", len(api_keys))
        for key in api_keys:
            logger.debug("Checking API key: %s", key.hashed_key)
            if bcrypt.checkpw(
                api_key.encode("utf-8"),
                key.hashed_key.encode("utf-8"),
            ):
                logger.debug("API key matched for user: %s", key.user.username)
                if key.user.disabled:
                    logger.warning("User %s is disabled", key.user.username)
                    raise HTTPException(
                        status_code=400,
                        detail="User account is disabled",
                    )
                return key.user
        logger.warning("No matching API key found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API key"},
        )
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    logger.debug("No API key provided, falling back to JWT token")
    try:
        username = verify_token(token)
        if not username:
            logger.warning("Invalid token: no username found")
            raise ValueError("Invalid token")
        user = await User.get(username=username)
        if not user:
            logger.warning("User %s not found", username)
            raise ValueError(f"User {username} not found")
        if user.disabled:
            logger.warning("User %s is disabled", username)
            raise HTTPException(
                status_code=400,
                detail="User account is disabled",
            )
    except PyJWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err
    except HTTPException as err:
        raise err
    except ValueError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err),
        ) from err
    except Exception as err:
        logger.error("JWT token validation failed: %s", err)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err
    return user
