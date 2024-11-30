import asyncio
from asyncio import AbstractEventLoop
from collections.abc import Callable
from typing import TYPE_CHECKING

from aiohttp import ClientError, ClientSession

from loadtestgui.base import StressClient

if TYPE_CHECKING:
    from concurrent.futures import Future


class AsyncStressClient(StressClient):
    __slots__ = (
        "loop",
        "url",
        "total_requests",
        "callback",
        "_completed_requests",
        "_load_test_future",
        "_refresh_rate",
        "_session",
    )

    def __init__(
        self,
        loop: AbstractEventLoop,
        url: str,
        total_requests: int,
        callback: Callable[[int, int], None],
    ) -> None:
        self.loop = loop
        self.url = url
        self.total_requests = total_requests
        self.callback = callback

        self._completed_requests = 0
        self._load_test_future: Future[None] | None = None
        self._refresh_rate = total_requests // 100

    def start(self) -> None:
        future = asyncio.run_coroutine_threadsafe(
            self._make_requests(), self.loop
        )
        self._load_test_future = future

    def cancel(self) -> None:
        if self._load_test_future:
            self.loop.call_soon_threadsafe(self._load_test_future.cancel)

    async def _make_requests(self) -> None:
        async with ClientSession(loop=self.loop) as session:
            responses = (
                self._get_url(session, self.url)
                for _ in range(self.total_requests)
            )
            await asyncio.gather(*responses)

    async def _get_url(self, session: ClientSession, url: str) -> None:
        try:
            await session.get(url)
        except ClientError as e:
            print(e)  # noqa: T201
        self._completed_requests += 1
        if (
            self._completed_requests % self._refresh_rate == 0
            or self._completed_requests == self.total_requests
        ):
            self.callback(self._completed_requests, self.total_requests)
