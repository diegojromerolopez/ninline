"""ANSI terminal box-drawing board renderer."""

from __future__ import annotations

from typing import List, Optional, Tuple

from .board import Board, Cell


class Renderer:
    COLOR_RESET = "\033[0m"
    COLOR_X = "\033[94m\033[1m"      # Bright Blue
    COLOR_O = "\033[91m\033[1m"      # Bright Red
    COLOR_GRID = "\033[90m"         # Dark Gray
    COLOR_HIGHLIGHT = "\033[92m\033[1m" # Bold Green for winning cells

    @classmethod
    def render(
        cls,
        board: Board,
        winning_line: Optional[List[Tuple[int, int]]] = None,
        use_color: bool = True,
    ) -> str:
        win_set = set(winning_line) if winning_line else set()
        lines: List[str] = []

        # Column headers
        header_col_nums = "    " + " ".join(f"{c:2d}" for c in range(board.cols))
        lines.append(header_col_nums)

        top_border = "   ┌" + "───┬" * (board.cols - 1) + "───┐"
        mid_border = "   ├" + "───┼" * (board.cols - 1) + "───┤"
        bot_border = "   └" + "───┴" * (board.cols - 1) + "───┘"

        lines.append(top_border)

        for r in range(board.rows):
            row_cells: List[str] = []
            for c in range(board.cols):
                cell = board.grid[r][c]
                symbol = cell.value if cell != Cell.EMPTY else " "
                if use_color:
                    if (r, c) in win_set:
                        formatted = f"{cls.COLOR_HIGHLIGHT}{symbol}{cls.COLOR_RESET}"
                    elif cell == Cell.X:
                        formatted = f"{cls.COLOR_X}{symbol}{cls.COLOR_RESET}"
                    elif cell == Cell.O:
                        formatted = f"{cls.COLOR_O}{symbol}{cls.COLOR_RESET}"
                    else:
                        formatted = " "
                else:
                    formatted = symbol
                row_cells.append(f" {formatted} ")

            row_str = f"{r:2d} │" + "│".join(row_cells) + "│"
            lines.append(row_str)
            if r < board.rows - 1:
                lines.append(mid_border)

        lines.append(bot_border)
        return "\n".join(lines)
