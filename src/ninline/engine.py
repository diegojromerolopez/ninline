"""Ray-casting line scanner and win/draw evaluator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .board import Board, Cell, GameStatus


@dataclass
class EvaluationResult:
    status: GameStatus
    winner: Optional[str]
    winning_line: Optional[List[Tuple[int, int]]]
    is_terminal: bool
    move_count: int
    rows: int
    cols: int
    win_length: int

    def to_dict(self) -> Dict[str, object]:
        return {
            "status": self.status.value,
            "winner": self.winner,
            "winning_line": [list(pt) for pt in self.winning_line] if self.winning_line else None,
            "is_terminal": self.is_terminal,
            "move_count": self.move_count,
            "rows": self.rows,
            "cols": self.cols,
            "win_length": self.win_length,
        }


class Evaluator:
    DIRECTIONS: Tuple[Tuple[int, int], ...] = (
        (0, 1),   # Horizontal
        (1, 0),   # Vertical
        (1, 1),   # Main diagonal
        (-1, 1),  # Anti-diagonal
    )

    @staticmethod
    def validate_win_length(rows: int, cols: int, win_length: int) -> None:
        max_dim = max(rows, cols)
        if win_length < 3 or win_length > max_dim:
            raise ValueError(f"Win length {win_length} must be between 3 and {max_dim}")

    @classmethod
    def evaluate(cls, board: Board, win_length: int) -> EvaluationResult:
        cls.validate_win_length(board.rows, board.cols, win_length)
        count_x = board.count_player(Cell.X)
        count_o = board.count_player(Cell.O)
        move_count = count_x + count_o

        # Standard alternating turn validity: X moves first, so count_x >= count_o and count_x - count_o <= 1
        if not (count_x == count_o or count_x == count_o + 1):
            return EvaluationResult(
                status=GameStatus.INVALID,
                winner=None,
                winning_line=None,
                is_terminal=True,
                move_count=move_count,
                rows=board.rows,
                cols=board.cols,
                win_length=win_length,
            )

        winner_found: Optional[Cell] = None
        winning_line: Optional[List[Tuple[int, int]]] = None
        winners_seen: set[Cell] = set()

        for r in range(board.rows):
            for c in range(board.cols):
                cell = board.grid[r][c]
                if cell == Cell.EMPTY:
                    continue
                for dr, dc in cls.DIRECTIONS:
                    # Check boundary for k steps
                    end_r = r + (win_length - 1) * dr
                    end_c = c + (win_length - 1) * dc
                    if not (0 <= end_r < board.rows and 0 <= end_c < board.cols):
                        continue

                    line_cells: List[Tuple[int, int]] = []
                    match = True
                    for step in range(win_length):
                        curr_r = r + step * dr
                        curr_c = c + step * dc
                        if board.grid[curr_r][curr_c] != cell:
                            match = False
                            break
                        line_cells.append((curr_r, curr_c))

                    if match:
                        winners_seen.add(cell)
                        if winner_found is None:
                            winner_found = cell
                            winning_line = line_cells

        if len(winners_seen) > 1:
            # Both players cannot both have winning lines
            return EvaluationResult(
                status=GameStatus.INVALID,
                winner=None,
                winning_line=None,
                is_terminal=True,
                move_count=move_count,
                rows=board.rows,
                cols=board.cols,
                win_length=win_length,
            )

        if winner_found is not None:
            # Verify turn count matches winner
            # If O won, count_x must equal count_o
            # If X won, count_x must equal count_o + 1
            if winner_found == Cell.O and count_x != count_o:
                return EvaluationResult(
                    status=GameStatus.INVALID,
                    winner=None,
                    winning_line=None,
                    is_terminal=True,
                    move_count=move_count,
                    rows=board.rows,
                    cols=board.cols,
                    win_length=win_length,
                )
            if winner_found == Cell.X and count_x != count_o + 1:
                return EvaluationResult(
                    status=GameStatus.INVALID,
                    winner=None,
                    winning_line=None,
                    is_terminal=True,
                    move_count=move_count,
                    rows=board.rows,
                    cols=board.cols,
                    win_length=win_length,
                )

            return EvaluationResult(
                status=GameStatus.WIN,
                winner=winner_found.value,
                winning_line=winning_line,
                is_terminal=True,
                move_count=move_count,
                rows=board.rows,
                cols=board.cols,
                win_length=win_length,
            )

        if move_count == board.rows * board.cols:
            return EvaluationResult(
                status=GameStatus.DRAW,
                winner=None,
                winning_line=None,
                is_terminal=True,
                move_count=move_count,
                rows=board.rows,
                cols=board.cols,
                win_length=win_length,
            )

        return EvaluationResult(
            status=GameStatus.IN_PROGRESS,
            winner=None,
            winning_line=None,
            is_terminal=False,
            move_count=move_count,
            rows=board.rows,
            cols=board.cols,
            win_length=win_length,
        )

    @classmethod
    def count_winning_lines(cls, rows: int, cols: int, win_length: int) -> Dict[str, int]:
        cls.validate_win_length(rows, cols, win_length)
        h_lines = rows * (cols - win_length + 1) if cols >= win_length else 0
        v_lines = cols * (rows - win_length + 1) if rows >= win_length else 0
        diag_lines = 0
        if rows >= win_length and cols >= win_length:
            per_diag = (rows - win_length + 1) * (cols - win_length + 1)
            diag_lines = 2 * per_diag  # main and anti-diagonal
        total = h_lines + v_lines + diag_lines
        return {
            "rows": rows,
            "cols": cols,
            "win_length": win_length,
            "total_cells": rows * cols,
            "total_winning_lines": total,
            "horizontal_lines": h_lines,
            "vertical_lines": v_lines,
            "diagonal_lines": diag_lines,
        }
