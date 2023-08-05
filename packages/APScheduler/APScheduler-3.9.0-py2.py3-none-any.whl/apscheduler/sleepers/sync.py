import threading
import time
from datetime import datetime
from typing import Optional


class SyncSleeper:
    _event: threading.Event

    def sleep_until(self, target: Optional[datetime]) -> None:
        timeout: Optional[float] = None
        if target is not None:
            timeout = target.timestamp() - time.time()
            if timeout <= 0:
                return

        self._event = threading.Event()
        self._event.wait(timeout)

    def wake_up(self) -> None:
        self._event.set()
