import asyncio
import importlib.util
import tkinter as tk
from queue import Queue
from tkinter import ttk
from typing import Any

from typing_extensions import Self

from load_testing_gui.stress_client import StressClient

ASYNC_MODE = bool(importlib.util.find_spec("aiohttp"))


class LoadTester(tk.Tk):
    def __init__(
        self,
        stress_client: StressClient,
        *,
        loop: asyncio.AbstractEventLoop | None = None,
        refresh_ms: int = 25,
        screen_name: str | None = None,
        base_name: str | None = None,
        class_name: str = "Tk",
        use_tk: bool = True,
        sync: bool = False,
        use: str | None = None,
    ) -> None:
        super().__init__(screen_name, base_name, class_name, use_tk, sync, use)
        self._stress_client = stress_client
        self._refresh_ms = refresh_ms
        self._loop = (
            asyncio.get_running_loop() if loop is None and ASYNC_MODE else loop
        )
        self._queue: Queue[Any] = Queue()

        self.title("URL requester")
        self._url_label = tk.Label(self, text="URL:")
        self._url_label.grid(column=0, row=0)

        self._url_field = tk.Entry(self, width=10)
        self._url_field.grid(column=1, row=0)

        self._request_label = tk.Label(self, text="Number of requests")
        self._request_label.grid(column=0, row=1)

        self._request_field = tk.Entry(self, width=10)
        self._request_field.grid(column=1, row=1)

        self._submit = ttk.Button(self, text="Submit")  # TODO: add command
        self._submit.grid(column=2, row=1)

        self._pb_label = tk.Label(self, text="Progress:")
        self._pb_label.grid(column=0, row=3)

        self._pb = ttk.Progressbar(
            self, orient="horizontal", length=200, mode="determinate"
        )
        self._pb.grid(column=1, row=3, columnspan=2)

        def _update_bar(self: Self, pct: int) -> None:
            if pct == 100:
                self._submit["text"] = "Submit"
            else:
                self._pb["value"] = pct
                # TODO: add self.after
