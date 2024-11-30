from abc import abstractmethod
from asyncio import AbstractEventLoop
from collections.abc import Callable
from typing import Protocol


class StressClient(Protocol):
    loop: AbstractEventLoop
    url: str
    total_requests: int
    callback: Callable[[int, int], None]

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def cancel(self) -> None: ...
