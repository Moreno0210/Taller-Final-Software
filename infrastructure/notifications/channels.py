
import asyncio

from application.ports.gateways import NotificationChannel


class EmailChannel(NotificationChannel):

    @property
    def name(self) -> str:
        return "email"

    async def send(
        self,
        destination: str,
        message: str
    ) -> None:

        print(
            f"SMTP: Enviando correo a {destination}: {message}"
        )

        await asyncio.sleep(0.01)


class SMSChannel(NotificationChannel):

    @property
    def name(self) -> str:
        return "sms"

    async def send(
        self,
        destination: str,
        message: str
    ) -> None:

        print(
            f"Twilio: Enviando SMS a {destination}: {message}"
        )

        await asyncio.sleep(0.01)


class WebhookChannel(NotificationChannel):

    @property
    def name(self) -> str:
        return "webhook"

    async def send(
        self,
        destination: str,
        message: str
    ) -> None:

        print(
            f"Webhook: Notificacion para {destination}: {message}"
        )

        await asyncio.sleep(0.01)
