# app/core/auth.py
import logging
import bcrypt
from datetime import datetime, timedelta, timezone
from app.config import settings
import jwt
from jwt import PyJWTError

logger = logging.getLogger("app.core.auth")


# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.

    Args:
        plain_password (str): The plain password to verify.
        hashed_password (str): The hashed password to verify against.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Creates an access token for a given user.

    Args:
        data (dict): Data to encode in the JWT.
        expires_delta (timedelta, optional): Time delta to set the expiration date of the token to. Defaults to None.

    Returns:
        bytes: The encoded JWT.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str):
    """
    Verifies a JWT token.

    Args:
        token (str): The JWT token to verify.

    Returns:
        str: The username if the token is valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        logger.debug("Token payload: %s", payload)
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except PyJWTError as err:
        logger.error("JWT error: %s", err)
        raise err
