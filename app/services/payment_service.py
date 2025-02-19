# app/services/payment_service.py
import logging
from typing import List
from datetime import datetime
from fastapi import HTTPException
from app.models import Payment


logger = logging.getLogger("app.services.payment_service")


class PaymentService:
    async def get_payments(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Payment]:
        """
        Fetches a list of payments from the database.

        Args:
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            List[Payment]: A list of Payment objects.

        Raises:
            HTTPException: If any error occurs while fetching the payments, a 500 error
                is raised with the error message.
        """
        try:
            return await Payment.all().offset(skip).limit(limit)
        except Exception as err:
            logger.error("Error fetching payments: %s", str(err))
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(err)}",
            ) from err
    
    async def get_all_payments(
        self,
    ) -> List[Payment]:
        """
        Fetches all payments from the database.

        Returns:
            List[Payment]: A list of all Payment objects.

        Raises:
            HTTPException: If any error occurs while fetching the payments, a 500 error
                is raised with the error message.
        """

        try:
            return await Payment.all()
        except Exception as err:
            logger.error("Error fetching payments: %s", str(err))
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(err)}",
            ) from err

    async def get_payment_by_interval(
        self,
        start_date: str,
        end_date: str,
    ) -> List[Payment]:
        """
        Fetches payments from the database that occurred within the given date range.

        Args:
            start_date: The start date of the range in ISO 8601 format.
            end_date: The end date of the range in ISO 8601 format.

        Returns:
            List[Payment]: A list of Payment objects that occurred within the given
                date range.

        Raises:
            HTTPException: If any error occurs while fetching the payments, a 500 error
                is raised with the error message.
        """
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            return await Payment.filter(date__range=(start, end))
        except Exception as err:
            logger.error("Error fetching payments by interval: %s", str(err))
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(err)}",
            ) from err
