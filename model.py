"""
model.py — Модель ігрового поля «Гра у 15»

Містить клас PuzzleModel, який зберігає стан поля 4×4,
забезпечує генерацію, перевірку розв'язності та виконання ходів.

Студент: Малиновський Борис Дмитрович | ІП-53 | КПІ 2026
"""

import random


class PuzzleModel:
    """
    Модель ігрового поля розміром SIZE×SIZE.

    Атрибути:
        board      (list[int])  — поточний стан поля (0 = порожня клітинка)
        blank_pos  (int)        — індекс порожньої клітинки (0..15)

    Константи:
        SIZE (int)       — розмір поля (4)
        GOAL (list[int]) — цільова впорядкована конфігурація
    """

    SIZE: int = 4
    GOAL: list[int] = list(range(1, 16)) + [0]

    def __init__(self) -> None:
        """Ініціалізує поле у вирішеному стані."""
        self.board: list[int] = list(self.GOAL)
        self.blank_pos: int = 15  # позиція порожньої клітинки

    # ── генерація ──────────────────────────────────────────────────────────

    def shuffle(self, moves: int = 200) -> None:
        """
        Перемішує поле заданою кількістю випадкових ходів.

        Параметри:
            moves (int) — кількість ходів для перемішування (за замовч. 200).

        Примітка: результат гарантовано є розв'язним, оскільки перемішування
                  виконується лише легальними ходами зі стартового GOAL-стану.
        """
        self.board = list(self.GOAL)
        self.blank_pos = 15
        prev: int = -1
        for _ in range(moves):
            neighbors = self._neighbors(self.blank_pos)
            # уникаємо повернення на попередній хід
            neighbors = [n for n in neighbors if n != prev]
            chosen = random.choice(neighbors)
            self._swap(self.blank_pos, chosen)
            prev = self.blank_pos
            self.blank_pos = chosen

    # ── внутрішні допоміжні методи ─────────────────────────────────────────

    def _neighbors(self, pos: int) -> list[int]:
        """
        Повертає список індексів клітинок, суміжних із pos.

        Параметри:
            pos (int) — індекс поточної клітинки (0..15).

        Повертає:
            list[int] — індекси сусідів (від 1 до 4 елементів).
        """
        r, c = divmod(pos, self.SIZE)
        result: list[int] = []
        if r > 0:              result.append(pos - self.SIZE)
        if r < self.SIZE - 1:  result.append(pos + self.SIZE)
        if c > 0:              result.append(pos - 1)
        if c < self.SIZE - 1:  result.append(pos + 1)
        return result

    def _swap(self, a: int, b: int) -> None:
        """
        Міняє місцями дві клітинки на полі.

        Параметри:
            a (int) — індекс першої клітинки.
            b (int) — індекс другої клітинки.
        """
        self.board[a], self.board[b] = self.board[b], self.board[a]

    # ── перевірки ──────────────────────────────────────────────────────────

    def is_solvable(self) -> bool:
        """
        Перевіряє, чи є поточна конфігурація розв'язною.

        Використовує теорему про парність перестановок і рядок порожньої клітинки:
          — якщо рядок порожньої клітинки від низу парний → кількість інверсій непарна;
          — якщо рядок непарний → кількість інверсій парна.

        Повертає:
            bool — True, якщо головоломка розв'язна.
        """
        tiles = [t for t in self.board if t != 0]
        inversions = sum(
            1
            for i in range(len(tiles))
            for j in range(i + 1, len(tiles))
            if tiles[i] > tiles[j]
        )
        blank_row_from_bottom = self.SIZE - self.blank_pos // self.SIZE
        if blank_row_from_bottom % 2 == 0:
            return inversions % 2 != 0
        else:
            return inversions % 2 == 0

    def is_solved(self) -> bool:
        """
        Перевіряє, чи вирішена головоломка.

        Повертає:
            bool — True, якщо поточний стан збігається з GOAL.
        """
        return self.board == self.GOAL

    def can_move(self, tile_pos: int) -> bool:
        """
        Перевіряє, чи можна перемістити плитку на позиції tile_pos.

        Параметри:
            tile_pos (int) — індекс плитки (0..15).

        Повертає:
            bool — True, якщо плитка є сусідом порожньої клітинки.
        """
        return tile_pos in self._neighbors(self.blank_pos)

    # ── виконання ходу ─────────────────────────────────────────────────────

    def move(self, tile_pos: int) -> bool:
        """
        Переміщує плитку з позиції tile_pos до порожньої клітинки.

        Параметри:
            tile_pos (int) — індекс плитки, яку необхідно перемістити.

        Повертає:
            bool — True, якщо хід був виконаний (плитка є сусідом); False інакше.
        """
        if not self.can_move(tile_pos):
            return False
        self._swap(tile_pos, self.blank_pos)
        self.blank_pos = tile_pos
        return True

    # ── доступ до стану ────────────────────────────────────────────────────

    def get_board(self) -> list[int]:
        """
        Повертає копію поточного стану поля.

        Повертає:
            list[int] — список із 16 елементів (0 = порожня клітинка).
        """
        return list(self.board)

    def set_board(self, board: list[int]) -> None:
        """
        Встановлює стан поля.

        Параметри:
            board (list[int]) — список із 16 цілих чисел (0 = порожня клітинка).
        """
        self.board = list(board)
        self.blank_pos = board.index(0)
