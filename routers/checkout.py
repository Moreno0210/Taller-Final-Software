
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from application.use_cases.checkout import (
    CheckoutCommand,
    InsufficientStockError,
    PaymentRejectedError
)

from api.dependencies import get_checkout_use_case


router = APIRouter(
    prefix="/checkout",
    tags=["Checkout"]
)


class CheckoutRequest(BaseModel):
    product_id: str
    quantity: int
    payment_token: str
    user_email: str
    notify_via: list[str] = Field(default_factory=list)


@router.post("/process")
async def process_checkout(
    request: CheckoutRequest,
    use_case=Depends(get_checkout_use_case)
):

    command = CheckoutCommand(
        product_id=request.product_id,
        quantity=request.quantity,
        payment_token=request.payment_token,
        user_email=request.user_email,
        notify_via=request.notify_via
    )

    try:
        order = await use_case.execute(command)
        return order

    except InsufficientStockError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except PaymentRejectedError as error:
        raise HTTPException(
            status_code=402,
            detail=str(error)
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error interno al procesar la compra"
        )
