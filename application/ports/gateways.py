
from abc import ABC, abstractmethod


class PaymentGateway(ABC):

    @abstractmethod
    async def charge(
        self,
        token: str,
        amount: float
    ) -> bool:
        pass


class NotificationChannel(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def send(
        self,
        destination: str,
        message: str
    ) -> None:
        pass


class InvoiceGenerator(ABC):

    @abstractmethod
    async def generate(
        self,
        order_id: str,
        amount: float
    ) -> bytes:
        pass
