
import asyncio
import pytest

from infrastructure.persistence.in_memory import InMemoryStore


@pytest.mark.asyncio
async def test_concurrent_reservations():

    store = InMemoryStore()

    results = await asyncio.gather(

        store.reserve_stock("PROD-A99", 7),

        store.reserve_stock("PROD-A99", 7)

    )

    assert results.count(True) == 1

    assert results.count(False) == 1

    assert await store.get_stock("PROD-A99") == 3


@pytest.mark.asyncio
async def test_release_stock():

    store = InMemoryStore()

    result = await store.reserve_stock(
        "PROD-A99",
        4
    )

    assert result is True

    await store.release_stock(
        "PROD-A99",
        4
    )

    assert await store.get_stock("PROD-A99") == 10
