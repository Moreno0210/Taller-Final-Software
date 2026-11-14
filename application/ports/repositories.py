
from abc import ABC, abstractmethod

from domain.entities.order import Order


class InventoryRepository(ABC):

    @abstractmethod
    async def reserve_stock(
        self,
        product_id: str,
        quantity: int
    ) -> bool:
        pass

    @abstractmethod
    async def release_stock(
        self,
        product_id: str,
        quantity: int
    ) -> None:
        pass


class OrderRepository(ABC):

    @abstractmethod
    async def save(self, order: Order) -> None:
        pass
