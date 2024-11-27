import asyncio
import tkinter as tk
from functools import partial
from queue import Queue
from tkinter import ttk
from typing import Any

from load_testing_gui.base import StressClient


class LoadTester(tk.Tk):
    def __init__(
        self,
        stress_client: type[StressClient],
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
        self.stress_client = stress_client
        self._stress_client: StressClient | None = None
        self._refresh_ms = refresh_ms
        self._loop = loop if loop else asyncio.get_running_loop()
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

        self._submit = ttk.Button(
            self, text="Submit", command=partial(_start, self)
        )
        self._submit.grid(column=2, row=1)

        self._pb_label = tk.Label(self, text="Progress:")
        self._pb_label.grid(column=0, row=3)

        self._pb = ttk.Progressbar(
            self, orient="horizontal", length=200, mode="determinate"
        )
        self._pb.grid(column=1, row=3, columnspan=2)


def _start(gui: "LoadTester") -> None:
    if gui._stress_client is None:
        gui._submit["text"] = "Cancel"
        test = gui.stress_client(
            gui._loop,  # type: ignore
            gui._url_field.get(),
            int(gui._request_field.get()),
            partial(_queue_update, gui),
        )
        gui.after(gui._refresh_ms, partial(_poll_queue, gui))
        test.start()
        gui._stress_client = test
    else:
        gui._stress_client.cancel()
        gui._stress_client = None
        gui._submit["text"] = "Submit"


def _queue_update(
    gui: "LoadTester", completed_requests: int, total_requests: int
) -> None:
    gui._queue.put(int(completed_requests / total_requests * 100))


def _poll_queue(gui: "LoadTester") -> None:  # type: ignore
    if not gui._queue.empty():
        percent_complete = gui._queue.get()
        _update_bar(gui, percent_complete)
    elif gui._stress_client:
        gui.after(gui._refresh_ms, partial(_poll_queue, gui))


def _update_bar(gui: "LoadTester", pct: int) -> None:
    if pct == 100:
        gui._stress_client = None
        gui._submit["text"] = "Submit"
    else:
        gui._pb["value"] = pct
        gui.after(gui._refresh_ms, partial(_poll_queue, gui))
