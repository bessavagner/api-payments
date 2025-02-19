import logging
from datetime import timedelta

import bcrypt

from fastapi import Request
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm


from app.config import settings
from app.dependencies import limiter
from app.core.auth import create_access_token
from app.models import User
from app.core.auth import verify_password

from app.schemas import UserCreate

logger = logging.getLogger("app.api.auth")
router = APIRouter()


@router.post("/register", status_code=201)
@limiter.limit("10/minute")
async def register(request: Request, user: UserCreate):
    # Check if username or email already exists
    """
    Registers a new user.

    :param request: The FastAPI request object
    :param user: The user to register
    :return: A JSON response with a success message
    :raises HTTPException: If the username or email already exists
    """
    logger.debug(user)
    existing_user = await User.filter(username=user.username).first()
    if existing_user:
        logger.error("Username %s already registered", user.username)
        raise HTTPException(
            status_code=400,
            detail="Username already registered",
        )
    existing_email = await User.filter(email=user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")
    await User.create(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    return {"msg": "User registered successfully"}


@router.post("/token")
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Authenticates a user and returns a JWT access token.

    :param request: The FastAPI request object
    :param form_data: The form data containing the username and password
    :return: A JSON response with the access token and its type
    :raises HTTPException: If the username or password is incorrect, or if the user is disabled
    """

    logger.debug("Login attempt for user %s", form_data.username)
    user = await User.get_or_none(username=form_data.username)
    logger.debug(user)
    logger.debug(request)
    logger.debug(form_data)
    if (
        not user
        or user.disabled
        or not verify_password(
            form_data.password,
            user.hashed_password,
        )
    ):
        logger.warning("Failed login attempt for user %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    logger.info("User %s logged in successfully", form_data.username)
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
