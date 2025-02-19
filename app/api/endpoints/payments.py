# app/api/endpoints/payments.py
from fastapi import Request, APIRouter, Depends


from app.services.payment_service import PaymentService
from app.schemas import PaymentSchema
from app.dependencies import get_current_user, limiter
from app.models import User

router = APIRouter()
payment_service = PaymentService()

@router.get("/", response_model=list[PaymentSchema])
@limiter.limit("20/minute")
async def read_payments(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves a paginated list of payments.

    This endpoint fetches a list of payments from the database with optional
    pagination. It requires authentication and is rate-limited to 10 requests
    per minute.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): Number of records to skip. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        current_user (User): The authenticated user making the request.

    Returns:
        List[PaymentSchema]: A list of payment records.

    Raises:
        HTTPException: If any error occurs while fetching the payments.
    """
    payments = await payment_service.get_payments(
        skip=skip,
        limit=limit,
    )
    return payments

@router.get("/all", response_model=list[PaymentSchema])
@limiter.limit("20/minute")
async def read_payments(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves all payment records.

    This endpoint fetches all available payment records from the database.
    It requires authentication and is rate-limited to 10 requests per minute.

    Args:
        request (Request): The FastAPI request object.
        current_user (User): The authenticated user making the request.

    Returns:
        List[PaymentSchema]: A list of all payment records.

    Raises:
        HTTPException: If any error occurs while fetching the payments.
    """

    payments = await payment_service.get_all_payments()
    return payments

@router.get("/interval", response_model=list[PaymentSchema])
@limiter.limit("20/minute")
async def read_payment_by_interval(
    request: Request,
    start_date: str,
    end_date: str,
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves payments that occurred within a given date range.

    This endpoint fetches a list of payments from the database that occurred
    within the given date range. It requires authentication and is rate-limited
    to 10 requests per minute.

    Args:
        request (Request): The FastAPI request object.
        start_date (str): The start date of the range in ISO 8601 format.
        end_date (str): The end date of the range in ISO 8601 format.
        current_user (User): The authenticated user making the request.

    Returns:
        List[PaymentSchema]: A list of payment records that occurred within the given
            date range.

    Raises:
        HTTPException: If any error occurs while fetching the payments.
    """
    payments = await payment_service.get_payment_by_interval(
        start_date,
        end_date,
    )
    return payments
