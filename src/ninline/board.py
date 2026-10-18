"""Board domain model, serialization, and boundary checks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class Cell(str, Enum):
    EMPTY = "."
    X = "X"
    O = "O"


class GameStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    WIN = "WIN"
    DRAW = "DRAW"
    INVALID = "INVALID"


@dataclass
class Board:
    rows: int
    cols: int
    grid: List[List[Cell]]

    @classmethod
    def create(cls, rows: int, cols: int) -> Board:
        if rows < 3 or cols < 3 or rows > 50 or cols > 50:
            raise ValueError(f"Board dimensions must be between 3 and 50. Got {rows}x{cols}")
        grid = [[Cell.EMPTY for _ in range(cols)] for _ in range(rows)]
        return cls(rows=rows, cols=cols, grid=grid)

    @classmethod
    def parse(cls, serialized: str) -> Board:
        if not serialized:
            raise ValueError("Serialized board cannot be empty")
        row_strs = serialized.split("|")
        rows = len(row_strs)
        cols = len(row_strs[0])
        if rows < 3 or cols < 3 or rows > 50 or cols > 50:
            raise ValueError(f"Board dimensions must be between 3 and 50. Got {rows}x{cols}")

        grid: List[List[Cell]] = []
        for r_idx, row_str in enumerate(row_strs):
            if len(row_str) != cols:
                raise ValueError(f"Inconsistent column count at row {r_idx}: expected {cols}, got {len(row_str)}")
            row_cells: List[Cell] = []
            for ch in row_str:
                if ch == "X":
                    row_cells.append(Cell.X)
                elif ch == "O":
                    row_cells.append(Cell.O)
                elif ch == ".":
                    row_cells.append(Cell.EMPTY)
                else:
                    raise ValueError(f"Invalid cell character: '{ch}'")
            grid.append(row_cells)
        return cls(rows=rows, cols=cols, grid=grid)

    def serialize(self) -> str:
        return "|".join("".join(cell.value for cell in row) for row in self.grid)

    def is_in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get(self, row: int, col: int) -> Cell:
        if not self.is_in_bounds(row, col):
            raise IndexError(f"Cell ({row}, {col}) out of bounds for {self.rows}x{self.cols}")
        return self.grid[row][col]

    def set(self, row: int, col: int, cell: Cell) -> None:
        if not self.is_in_bounds(row, col):
            raise IndexError(f"Cell ({row}, {col}) out of bounds for {self.rows}x{self.cols}")
        self.grid[row][col] = cell

    def is_empty(self, row: int, col: int) -> bool:
        return self.get(row, col) == Cell.EMPTY

    def count_moves(self) -> int:
        return sum(1 for row in self.grid for cell in row if cell != Cell.EMPTY)

    def count_player(self, player: Cell) -> int:
        return sum(1 for row in self.grid for cell in row if cell == player)

    def get_empty_cells(self) -> List[Tuple[int, int]]:
        res: List[Tuple[int, int]] = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == Cell.EMPTY:
                    res.append((r, c))
        return res

    def clone(self) -> Board:
        return Board(
            rows=self.rows,
            cols=self.cols,
            grid=[list(row) for row in self.grid],
        )
