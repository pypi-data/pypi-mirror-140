import abc
import asyncio
from typing import Union


class Updater(abc.ABC):
    def __init__(self, delay: Union[int, float]):
        self.delay: Union[int, float] = delay or 1
        self._stopped: bool = False
        self._event: asyncio.Event = asyncio.Event()

    @property
    def delay(self) -> Union[int, float]:
        return self._delay

    @delay.setter
    def delay(self, value: Union[int, float]):
        self._delay = value

    async def start(self) -> None:
        self._event.clear()
        self._stopped = False
        while not self._stopped:
            try:
                await asyncio.wait_for(self._event.wait(), timeout=self.delay)
            except asyncio.TimeoutError:
                pass

            if not self._stopped:
                try:
                    await self._do_update()
                except Exception as e:
                    self.stop()
                    raise e

    def stop(self) -> None:
        self._stopped = True
        self._event.set()

    def dispose(self) -> None:
        self._do_dispose()

        if not self._stopped:
            self.stop()

        self._event = None

    @abc.abstractmethod
    async def _do_update(self) -> None:
        # for override
        pass

    @abc.abstractmethod
    def _do_dispose(self) -> None:
        # for override
        pass
