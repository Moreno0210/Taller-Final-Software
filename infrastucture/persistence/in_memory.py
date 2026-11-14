
import asyncio

from domain.entities.order import Order

from application.ports.repositories import (
    InventoryRepository,
    OrderRepository
)


class InMemoryStore(InventoryRepository, OrderRepository):

    def __init__(self):

        self._inventory = {
            "PROD-A99": 10,
            "PROD-B88": 2
        }

        self._orders = {}

        self._lock = asyncio.Lock()

    async def reserve_stock(
        self,
        product_id: str,
        quantity: int
    ) -> bool:

        async with self._lock:

            current_stock = self._inventory.get(
                product_id, 0
            )

            if quantity <= 0 or current_stock < quantity:
                return False

            self._inventory[product_id] = (
                current_stock - quantity
            )

            return True

    async def release_stock(
        self,
        product_id: str,
        quantity: int
    ) -> None:

        async with self._lock:

            current_stock = self._inventory.get(
                product_id, 0
            )

            self._inventory[product_id] = (
                current_stock + quantity
            )

    async def save(self, order: Order) -> None:

        async with self._lock:

            self._orders[order.order_id] = order

    async def get_stock(self, product_id: str) -> int:

        async with self._lock:

            return self._inventory.get(product_id, 0)

    async def get_order(self, order_id: str):

        async with self._lock:

            return self._orders.get(order_id)
