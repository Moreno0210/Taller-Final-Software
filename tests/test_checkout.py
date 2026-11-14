
import pytest

from application.use_cases.checkout import (
    CheckoutUseCase,
    CheckoutCommand,
    PaymentRejectedError,
    InsufficientStockError
)

from application.ports.gateways import InvoiceGenerator

from infrastructure.persistence.in_memory import InMemoryStore

from infrastructure.payments.gateways import MockPaymentGateway


class FakeInvoiceGenerator(InvoiceGenerator):

    async def generate(
        self,
        order_id: str,
        amount: float
    ) -> bytes:

        return b"invoice"


def build_use_case(store):

    return CheckoutUseCase(
        inventory=store,
        orders=store,
        payment=MockPaymentGateway(),
        notification_channels=[],
        invoice_generator=FakeInvoiceGenerator()
    )


@pytest.mark.asyncio
async def test_checkout_success():

    store = InMemoryStore()

    use_case = build_use_case(store)

    result = await use_case.execute(
        CheckoutCommand(
            product_id="PROD-A99",
            quantity=2,
            payment_token="tok_ok",
            user_email="test@example.com",
            notify_via=[]
        )
    )

    assert result.quantity == 2

    assert result.total_amount == 199.98

    assert await store.get_stock("PROD-A99") == 8


@pytest.mark.asyncio
async def test_payment_failure():

    store = InMemoryStore()

    use_case = build_use_case(store)

    with pytest.raises(PaymentRejectedError):

        await use_case.execute(
            CheckoutCommand(
                product_id="PROD-A99",
                quantity=2,
                payment_token="declined",
                user_email="test@example.com",
                notify_via=[]
            )
        )

    assert await store.get_stock("PROD-A99") == 10


@pytest.mark.asyncio
async def test_insufficient_stock():

    store = InMemoryStore()

    use_case = build_use_case(store)

    with pytest.raises(InsufficientStockError):

        await use_case.execute(
            CheckoutCommand(
                product_id="PROD-A99",
                quantity=11,
                payment_token="tok_ok",
                user_email="test@example.com",
                notify_via=[]
            )
        )
