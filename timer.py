"""
timer.py — Ігровий таймер

Містить клас GameTimer для відстеження часу, витраченого на розв'язання
головоломки. Підтримує запуск, зупинку, скидання та форматований вивід.

Студент: Малиновський Борис Дмитрович | ІП-53 | КПІ 2026
"""

import time


class GameTimer:
    """
    Таймер із можливістю зупинки та продовження.

    Атрибути:
        _start   (float | None) — мітка часу останнього виклику start().
        _elapsed (float)        — накопичений час у секундах.
        _running (bool)         — True, якщо таймер зараз активний.
    """

    def __init__(self) -> None:
        """Ініціалізує таймер у зупиненому стані (elapsed = 0)."""
        self._start:   float | None = None
        self._elapsed: float        = 0.0
        self._running: bool         = False

    def start(self) -> None:
        """
        Запускає таймер.

        Якщо таймер вже запущений — не змінює стан (повторний виклик безпечний).
        """
        if not self._running:
            self._start   = time.time()
            self._running = True

    def stop(self) -> None:
        """
        Зупиняє таймер та зберігає накопичений час.

        Якщо таймер вже зупинений — не змінює стан.
        """
        if self._running and self._start is not None:
            self._elapsed += time.time() - self._start
        self._running = False

    def reset(self) -> None:
        """Скидає таймер до початкового стану (elapsed = 0, зупинений)."""
        self._start   = None
        self._elapsed = 0.0
        self._running = False

    def elapsed(self) -> float:
        """
        Повертає повний час у секундах (включно з поточним інтервалом, якщо активний).

        Повертає:
            float — кількість секунд із моменту першого запуску.
        """
        if self._running and self._start is not None:
            return self._elapsed + (time.time() - self._start)
        return self._elapsed

    def format(self) -> str:
        """
        Повертає час у форматі ХВ:СЕК (наприклад, «03:45»).

        Повертає:
            str — рядок формату «MM:SS».
        """
        s = int(self.elapsed())
        return f"{s // 60:02d}:{s % 60:02d}"
