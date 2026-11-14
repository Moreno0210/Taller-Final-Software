
from application.use_cases.checkout import CheckoutUseCase

from infrastructure.persistence.in_memory import InMemoryStore

from infrastructure.payments.gateways import MockPaymentGateway

from infrastructure.notifications.channels import (
    EmailChannel,
    SMSChannel,
    WebhookChannel
)

from infrastructure.documents.invoice import ProcessInvoiceGenerator


# Instancias compartidas de infraestructura

_store = InMemoryStore()

_payment = MockPaymentGateway()

_channels = [
    EmailChannel(),
    SMSChannel(),
    WebhookChannel()
]

_invoice = ProcessInvoiceGenerator()


def get_checkout_use_case() -> CheckoutUseCase:

    return CheckoutUseCase(
        inventory=_store,
        orders=_store,
        payment=_payment,
        notification_channels=_channels,
        invoice_generator=_invoice
    )
