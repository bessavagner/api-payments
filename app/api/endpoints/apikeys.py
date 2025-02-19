import logging
import secrets
import bcrypt
from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.models import ApiKey

logger = logging.getLogger("app.api.apikeys")
router = APIRouter()


@router.post("/generate", status_code=201)
async def generate_api_key(current_user=Depends(get_current_user)):
    """
    Generates a new API key for the authenticated user.

    **Authentication:** Required (JWT)

    **Response Codes:**
    *   `201 Created`: API key generated successfully.
    *   `401 Unauthorized`: Authentication required.

    **Example Response (201):**
    """
    logger.debug(
        "Generating a new API key for user: %s",
        current_user.username,
    )
    raw_api_key = secrets.token_urlsafe(32)
    key_prefix = raw_api_key[:10]
    hashed_api_key = bcrypt.hashpw(
        raw_api_key.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")
    await ApiKey.create(
        user=current_user,
        hashed_key=hashed_api_key,
        key_prefix=key_prefix,
    )
    logger.debug("API key generated: %s", raw_api_key)
    return {"api_key": raw_api_key, "msg": "API key generated successfully"}
