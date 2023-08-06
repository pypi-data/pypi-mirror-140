import asyncio
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from asyncio import Future


class StateFuture:
    _fut: Optional["Future"] = None

    def __init__(self, loop=None) -> None:
        self._loop = loop or asyncio.get_event_loop()

    def __await__(self):
        return self.fut.__await__()

    @property
    def fut(self) -> "Future":
        if not self._fut:
            self._fut = self._loop.create_future()
        return self._fut

    def reset(self):
        self._fut = None

    def set_result(self, value, check_done=False):
        is_set_result = True

        if check_done and self.fut.done():
            is_set_result = False

        if is_set_result:
            self._loop.call_soon_threadsafe(self.fut.set_result, value)

    def __getattr__(self, name):
        return getattr(self.fut, name)
