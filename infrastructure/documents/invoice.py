
import math
import asyncio

from concurrent.futures import ProcessPoolExecutor

from application.ports.gateways import InvoiceGenerator


def build_manifest(
    order_id: str,
    amount: float
) -> bytes:

    iterations = 5_000_000

    result = 0.0

    for i in range(iterations):

        result += math.sqrt(i) * math.sin(i)

    manifest_data = (
        f"ORDER:{order_id}|"
        f"TOTAL:{amount}|"
        f"HASH:{result}"
    )

    return manifest_data.encode("utf-8")


class ProcessInvoiceGenerator(InvoiceGenerator):

    def __init__(self, executor=None):

        self.executor = (
            executor
            if executor is not None
            else ProcessPoolExecutor(max_workers=2)
        )

    async def generate(
        self,
        order_id: str,
        amount: float
    ) -> bytes:

        loop = asyncio.get_running_loop()

        result = await loop.run_in_executor(
            self.executor,
            build_manifest,
            order_id,
            amount
        )

        return result
