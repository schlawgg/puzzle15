"""
solver.py — Розв'язувач головоломки «Гра у 15» методом A*

Реалізує клас PuzzleSolver з евристиками Manhattan Distance
та Linear Conflict для пошуку оптимального розв'язку.

Студент: Малиновський Борис Дмитрович | ІП-53 | КПІ 2026
"""

import heapq


class PuzzleSolver:
    """
    Розв'язувач головоломки 15 за алгоритмом A*.

    Евристична функція: Manhattan Distance + Linear Conflict.
    Це допустима (admissible) та консистентна евристика, яка гарантує
    знаходження оптимального розв'язку.

    Складність: O(b^d), де b — коефіцієнт розгалуження (~3), d — глибина.
    Обмеження: 200 000 вузлів (для захисту від занадто складних конфігурацій).
    """

    SIZE: int = 4
    GOAL: list[int] = list(range(1, 16)) + [0]
    NODE_LIMIT: int = 200_000

    # ── евристики ──────────────────────────────────────────────────────────

    @staticmethod
    def _manhattan(board: list[int]) -> int:
        """
        Обчислює суму манхеттенських відстаней кожної плитки до її цільової позиції.

        Параметри:
            board (list[int]) — поточний стан поля (16 елементів).

        Повертає:
            int — значення евристики h(n) ≥ 0.
        """
        dist = 0
        for idx, val in enumerate(board):
            if val == 0:
                continue
            goal_idx = val - 1  # цільовий індекс для плитки зі значенням val
            dist += abs(idx // 4 - goal_idx // 4) + abs(idx % 4 - goal_idx % 4)
        return dist

    @staticmethod
    def _linear_conflict(board: list[int]) -> int:
        """
        Обчислює доповнення евристики — «лінійний конфлікт».

        Два плитки утворюють лінійний конфлікт, якщо обидві знаходяться
        у своєму цільовому рядку (або стовпці), але їхній відносний порядок
        є оберненим. Кожен конфлікт додає 2 до нижньої межі.

        Параметри:
            board (list[int]) — поточний стан поля (16 елементів).

        Повертає:
            int — значення лінійного конфлікту (кратне 2).
        """
        lc = 0
        SIZE = 4
        # перевірка по рядках
        for r in range(SIZE):
            row = board[r * SIZE:(r + 1) * SIZE]
            for i in range(SIZE):
                ti = row[i]
                if ti == 0:
                    continue
                if (ti - 1) // SIZE != r:  # плитка ti не належить цьому рядку
                    continue
                for j in range(i + 1, SIZE):
                    tj = row[j]
                    if tj == 0:
                        continue
                    if (tj - 1) // SIZE == r and ti > tj:
                        lc += 2
        # перевірка по стовпцях
        for c in range(SIZE):
            col = board[c::SIZE]
            for i in range(SIZE):
                ti = col[i]
                if ti == 0:
                    continue
                if (ti - 1) % SIZE != c:  # плитка ti не належить цьому стовпцю
                    continue
                for j in range(i + 1, SIZE):
                    tj = col[j]
                    if tj == 0:
                        continue
                    if (tj - 1) % SIZE == c and ti > tj:
                        lc += 2
        return lc

    def _h(self, board: tuple[int, ...]) -> int:
        """
        Комбінована евристична функція h(n) = Manhattan + LinearConflict.

        Параметри:
            board (tuple[int, ...]) — стан поля у вигляді кортежу.

        Повертає:
            int — нижня межа кількості ходів до розв'язку.
        """
        b = list(board)
        return self._manhattan(b) + self._linear_conflict(b)

    # ── основний метод ─────────────────────────────────────────────────────

    def solve(self, board: list[int]) -> list[list[int]] | None:
        """
        Знаходить оптимальну послідовність станів від початкового до вирішеного.

        Алгоритм A* із пріоритетною чергою (min-heap).
        Кожен вузол: (f, g, стан, шлях), де f = g + h(стан).

        Параметри:
            board (list[int]) — початковий стан поля (16 елементів).

        Повертає:
            list[list[int]] | None — список станів від початку до кінця,
                                     або None якщо розв'язок не знайдено
                                     в межах NODE_LIMIT вузлів.
        """
        goal  = tuple(self.GOAL)
        start = tuple(board)

        if start == goal:
            return [list(board)]

        open_heap: list = []
        heapq.heappush(open_heap, (self._h(start), 0, start, [start]))
        # visited: стан → мінімальна вартість g, що дозволила до нього дійти
        visited: dict[tuple, int] = {start: 0}
        limit = self.NODE_LIMIT

        while open_heap and limit > 0:
            limit -= 1
            f, g, state, path = heapq.heappop(open_heap)

            if state == goal:
                return [list(s) for s in path]

            blank = state.index(0)
            r, c  = divmod(blank, 4)

            neighbors_pos: list[int] = []
            if r > 0: neighbors_pos.append(blank - 4)
            if r < 3: neighbors_pos.append(blank + 4)
            if c > 0: neighbors_pos.append(blank - 1)
            if c < 3: neighbors_pos.append(blank + 1)

            for nb in neighbors_pos:
                lst = list(state)
                lst[blank], lst[nb] = lst[nb], lst[blank]
                ns = tuple(lst)
                ng = g + 1
                if ns not in visited or visited[ns] > ng:
                    visited[ns] = ng
                    heapq.heappush(open_heap, (ng + self._h(ns), ng, ns, path + [ns]))

        return None  # розв'язок не знайдено в межах NODE_LIMIT
