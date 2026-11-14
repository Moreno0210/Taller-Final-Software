
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.dependencies import get_checkout_use_case

from application.use_cases.checkout import (
    CheckoutUseCase,
    CheckoutCommand,
    InsufficientStockError,
    PaymentRejectedError
)


router = APIRouter()


class CheckoutRequest(BaseModel):

    product_id: str

    quantity: int = Field(gt=0)

    payment_token: str

    user_email: str

    notify_via: list[str] = Field(default_factory=list)


@router.post("/process")
async def process_checkout(

    payload: CheckoutRequest,

    use_case: CheckoutUseCase = Depends(
        get_checkout_use_case
    )

):

    command = CheckoutCommand(
        product_id=payload.product_id,
        quantity=payload.quantity,
        payment_token=payload.payment_token,
        user_email=payload.user_email,
        notify_via=payload.notify_via
    )

    try:

        order = await use_case.execute(command)

        return {
            "status": "success",
            "order_id": order.order_id,
            "total": order.total_amount
        }

    except InsufficientStockError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except PaymentRejectedError as exc:

        raise HTTPException(
            status_code=402,
            detail=str(exc)
        ) from exc

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except RuntimeError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc
