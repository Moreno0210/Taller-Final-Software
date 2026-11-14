
from dataclasses import dataclass
from uuid import uuid4

from domain.entities.order import Order

from application.ports.repositories import (
    InventoryRepository,
    OrderRepository
)

from application.ports.gateways import (
    PaymentGateway,
    NotificationChannel,
    InvoiceGenerator
)


class InsufficientStockError(Exception):
    pass


class PaymentRejectedError(Exception):
    pass


@dataclass
class CheckoutCommand:

    product_id: str
    quantity: int
    payment_token: str
    user_email: str
    notify_via: list[str]


class CheckoutUseCase:

    PRICE_PER_UNIT = 99.99

    def __init__(
        self,
        inventory: InventoryRepository,
        orders: OrderRepository,
        payment: PaymentGateway,
        notification_channels: list[NotificationChannel],
        invoice_generator: InvoiceGenerator
    ):

        self.inventory = inventory
        self.orders = orders
        self.payment = payment

        self.notification_channels = {
            channel.name: channel
            for channel in notification_channels
        }

        self.invoice_generator = invoice_generator

    async def execute(self, command: CheckoutCommand) -> Order:

        if command.quantity <= 0:
            raise ValueError(
                "La cantidad debe ser mayor que cero"
            )

        selected_channels = []

        for channel_name in command.notify_via:

            channel = self.notification_channels.get(channel_name)

            if channel is None:
                raise ValueError(
                    f"Canal no soportado: {channel_name}"
                )

            selected_channels.append(channel)

        reserved = await self.inventory.reserve_stock(
            command.product_id,
            command.quantity
        )

        if not reserved:
            raise InsufficientStockError(
                "Stock insuficiente"
            )

        total = round(
            command.quantity * self.PRICE_PER_UNIT,
            2
        )

        try:

            payment_ok = await self.payment.charge(
                command.payment_token,
                total
            )

        except Exception:

            await self.inventory.release_stock(
                command.product_id,
                command.quantity
            )

            raise

        if not payment_ok:

            await self.inventory.release_stock(
                command.product_id,
                command.quantity
            )

            raise PaymentRejectedError(
                "Pago rechazado por la pasarela"
            )

        order = Order(
            order_id=f"TX-{uuid4().hex[:12].upper()}",
            product_id=command.product_id,
            quantity=command.quantity,
            total_amount=total,
            user_email=command.user_email
        )

        await self.orders.save(order)

        await self.invoice_generator.generate(
            order.order_id,
            total
        )

        for channel in selected_channels:

            await channel.send(
                command.user_email,
                "Su orden ha sido procesada"
            )

        return order
