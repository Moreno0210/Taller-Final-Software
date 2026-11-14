
import httpx

from application.ports.gateways import PaymentGateway
from core.config import settings


class MockPaymentGateway(PaymentGateway):

    async def charge(
        self,
        token: str,
        amount: float
    ) -> bool:

        return token != "declined"


class StripePaymentGateway(PaymentGateway):

    def __init__(self, api_key=None):

        self.api_key = (
            api_key
            if api_key is not None
            else settings.STRIPE_API_KEY
        )

    async def charge(
        self,
        token: str,
        amount: float
    ) -> bool:

        if not self.api_key:
            raise RuntimeError(
                "STRIPE_API_KEY no está configurada"
            )

        payload = {
            "token": token,
            "amount": amount
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        try:

            async with httpx.AsyncClient(timeout=5.0) as client:

                response = await client.post(
                    "https://api.stripe.com/v1/charges",
                    data=payload,
                    headers=headers
                )

                return response.is_success

        except httpx.HTTPError:

            return False
