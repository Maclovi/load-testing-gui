import asyncio
from asyncio import AbstractEventLoop
from threading import Thread

from load_testing_gui.async_client import AsyncStressClient as StressClient
from load_testing_gui.tk_gui import LoadTester


class ThreadedEventLoop(Thread):
    def __init__(self, loop: AbstractEventLoop) -> None:
        super().__init__()
        self._loop = loop
        self.daemon = True

    def run(self) -> None:
        self._loop.run_forever()


def main() -> None:
    loop = asyncio.new_event_loop()
    asyncio_thread = ThreadedEventLoop(loop)
    asyncio_thread.start()

    app = LoadTester(StressClient, loop=loop)
    app.mainloop()


if __name__ == "__main__":
    main()
