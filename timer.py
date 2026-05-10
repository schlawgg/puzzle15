import time


class GameTimer:
    def __init__(self) -> None:
        self._start:   float | None = None
        self._elapsed: float        = 0.0
        self._running: bool         = False

    def start(self) -> None:
        if not self._running:
            self._start   = time.time()
            self._running = True

    def stop(self) -> None:
        if self._running and self._start is not None:
            self._elapsed += time.time() - self._start
        self._running = False

    def reset(self) -> None:
        self._start   = None
        self._elapsed = 0.0
        self._running = False

    def elapsed(self) -> float:
        if self._running and self._start is not None:
            return self._elapsed + (time.time() - self._start)
        return self._elapsed

    def format(self) -> str:
        s = int(self.elapsed())
        return f"{s // 60:02d}:{s % 60:02d}"
