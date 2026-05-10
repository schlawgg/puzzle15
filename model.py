import random


class PuzzleModel:
    SIZE: int = 4
    GOAL: list[int] = list(range(1, 16)) + [0]

    def __init__(self) -> None:
        self.board: list[int] = list(self.GOAL)
        self.blank_pos: int = 15

    #генерація

    def shuffle(self, moves: int = 200) -> None:
        self.board = list(self.GOAL)
        self.blank_pos = 15
        prev: int = -1
        for _ in range(moves):
            neighbors = self._neighbors(self.blank_pos)
            neighbors = [n for n in neighbors if n != prev]
            chosen = random.choice(neighbors)
            self._swap(self.blank_pos, chosen)
            prev = self.blank_pos
            self.blank_pos = chosen

    #внутрішні допоміжні методи

    def _neighbors(self, pos: int) -> list[int]:
        r, c = divmod(pos, self.SIZE)
        result: list[int] = []
        if r > 0:              result.append(pos - self.SIZE)
        if r < self.SIZE - 1:  result.append(pos + self.SIZE)
        if c > 0:              result.append(pos - 1)
        if c < self.SIZE - 1:  result.append(pos + 1)
        return result

    def _swap(self, a: int, b: int) -> None:
        self.board[a], self.board[b] = self.board[b], self.board[a]

    #перевірки

    def is_solvable(self) -> bool:
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
        return self.board == self.GOAL

    def can_move(self, tile_pos: int) -> bool:
        return tile_pos in self._neighbors(self.blank_pos)

    #виконання ходу

    def move(self, tile_pos: int) -> bool:
        if not self.can_move(tile_pos):
            return False
        self._swap(tile_pos, self.blank_pos)
        self.blank_pos = tile_pos
        return True

    #доступ до стану

    def get_board(self) -> list[int]:
        return list(self.board)

    def set_board(self, board: list[int]) -> None:
        self.board = list(board)
        self.blank_pos = board.index(0)
