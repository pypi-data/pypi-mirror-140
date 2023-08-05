import time
from datetime import datetime
from typing import Optional

import anyio


class AsyncSleeper:
    _event: anyio.Event

    async def sleep_until(self, target: datetime) -> None:
        timeout: Optional[float] = None
        if target is not None:
            timeout = target.timestamp() - time.time()
            if timeout <= 0:
                return

        self._event = anyio.Event()
        with anyio.move_on_after(timeout):
            await self._event.wait()

    def wake_up(self) -> None:
        self._event.set()
