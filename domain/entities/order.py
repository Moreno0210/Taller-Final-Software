
from dataclasses import dataclass


@dataclass
class Order:

    order_id: str
    product_id: str
    quantity: int
    total_amount: float
    user_email: str
