import asyncio
from abc import ABC
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Coroutine, List, Sequence, TypeVar

import httpx
import nest_asyncio

nest_asyncio.apply()

DEFAULT_BASE_URL = "https://api.pngme.com/beta"

T = TypeVar("T")


def with_concurrency_limit(
    coroutines: Sequence[Coroutine[None, None, T]], concurrency: int
) -> List[Coroutine[None, None, T]]:
    """Decorate coroutines to limit concurrency.

    Enforces a limit on the number of coroutines that can run concurrently in higher
    level asyncio-compatible concurrency managers like asyncio.gather(coroutines),
    asyncio.as_completed(coroutines), etc.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def _with_concurrency_limit(coroutine: Coroutine[None, None, T]) -> T:
        async with semaphore:
            return await coroutine

    return [_with_concurrency_limit(coroutine) for coroutine in coroutines]


class BaseClient(ABC):
    def __init__(
        self,
        access_token: str,
        concurrency_limit: int = 50,
        base_url: str = DEFAULT_BASE_URL,
    ):
        """Client SDK to interact with Pngme financial report resources.

        Args:
            access_token: API key from https://admin.pngme.com
            concurrency_limit: maximum concurrency for internal pagination handling
            base_url: root url for API resources
        """
        self.access_token = access_token
        self.concurrency_limit = concurrency_limit
        self.base_url = base_url

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Configure a session with authorization and connection settings."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        transport = httpx.AsyncHTTPTransport(retries=10)
        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=30,
            transport=transport,
        ) as session:
            yield session
