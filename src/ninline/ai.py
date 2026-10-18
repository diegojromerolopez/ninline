"""Alpha-Beta Minimax AI and heuristic search."""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

from .board import Board, Cell, GameStatus
from .engine import Evaluator


class AI:
    @staticmethod
    def opponent(player: Cell) -> Cell:
        return Cell.O if player == Cell.X else Cell.X

    @classmethod
    def recommend_move(
        cls,
        board: Board,
        win_length: int,
        player: Cell,
        difficulty: str = "hard",
    ) -> Tuple[int, int, int]:
        empty_cells = board.get_empty_cells()
        if not empty_cells:
            raise ValueError("No available moves on board")

        opp = cls.opponent(player)

        # 1. Immediate Win check
        for r, c in empty_cells:
            board.set(r, c, player)
            eval_res = Evaluator.evaluate(board, win_length)
            board.set(r, c, Cell.EMPTY)
            if eval_res.status == GameStatus.WIN and eval_res.winner == player.value:
                return r, c, 100

        # 2. Immediate Block check
        for r, c in empty_cells:
            board.set(r, c, opp)
            eval_res = Evaluator.evaluate(board, win_length)
            board.set(r, c, Cell.EMPTY)
            if eval_res.status == GameStatus.WIN and eval_res.winner == opp.value:
                return r, c, 80

        if difficulty == "easy":
            r, c = random.choice(empty_cells)
            return r, c, 0

        # Sort candidate moves by proximity to center and neighbors
        cr, cc = (board.rows - 1) / 2.0, (board.cols - 1) / 2.0
        candidates = sorted(
            empty_cells,
            key=lambda pt: abs(pt[0] - cr) + abs(pt[1] - cc),
        )

        if len(candidates) <= 9 and (board.rows * board.cols <= 16 or len(candidates) <= 7):
            # Full Minimax with Alpha-Beta
            best_score = -999999
            best_move = candidates[0]
            alpha = -999999
            beta = 999999
            for r, c in candidates:
                board.set(r, c, player)
                score = cls._minimax(board, win_length, 0, False, player, opp, alpha, beta, max_depth=9)
                board.set(r, c, Cell.EMPTY)
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            return best_move[0], best_move[1], best_score

        # Heuristic search with depth <= 3 for larger boards
        max_depth = 2 if len(candidates) > 20 else 3
        best_score = -999999
        best_move = candidates[0]
        alpha = -999999
        beta = 999999
        subset = candidates[:min(14, len(candidates))]
        for r, c in subset:
            board.set(r, c, player)
            score = cls._minimax(board, win_length, 0, False, player, opp, alpha, beta, max_depth=max_depth)
            board.set(r, c, Cell.EMPTY)
            if score > best_score:
                best_score = score
                best_move = (r, c)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break

        return best_move[0], best_move[1], best_score

    @classmethod
    def _minimax(
        cls,
        board: Board,
        win_length: int,
        depth: int,
        is_maximizing: bool,
        player: Cell,
        opp: Cell,
        alpha: int,
        beta: int,
        max_depth: int,
    ) -> int:
        eval_res = Evaluator.evaluate(board, win_length)
        if eval_res.status == GameStatus.WIN:
            if eval_res.winner == player.value:
                return 100 - depth
            return -100 + depth
        if eval_res.status == GameStatus.DRAW:
            return 0
        if depth >= max_depth:
            return cls._heuristic_eval(board, win_length, player, opp)

        empty_cells = board.get_empty_cells()
        if not empty_cells:
            return 0

        # Proximity sorting
        cr, cc = (board.rows - 1) / 2.0, (board.cols - 1) / 2.0
        empty_cells.sort(key=lambda pt: abs(pt[0] - cr) + abs(pt[1] - cc))
        moves = empty_cells[:8]  # Branching limit for fast evaluation

        if is_maximizing:
            max_eval = -999999
            for r, c in moves:
                board.set(r, c, player)
                eval_val = cls._minimax(board, win_length, depth + 1, False, player, opp, alpha, beta, max_depth)
                board.set(r, c, Cell.EMPTY)
                max_eval = max(max_eval, eval_val)
                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = 999999
            for r, c in moves:
                board.set(r, c, opp)
                eval_val = cls._minimax(board, win_length, depth + 1, True, player, opp, alpha, beta, max_depth)
                board.set(r, c, Cell.EMPTY)
                min_eval = min(min_eval, eval_val)
                beta = min(beta, eval_val)
                if beta <= alpha:
                    break
            return min_eval

    @classmethod
    def _heuristic_eval(cls, board: Board, win_length: int, player: Cell, opp: Cell) -> int:
        score = 0
        cr, cc = (board.rows - 1) / 2.0, (board.cols - 1) / 2.0
        for r in range(board.rows):
            for c in range(board.cols):
                cell = board.grid[r][c]
                if cell == player:
                    score += int(10 - (abs(r - cr) + abs(c - cc)))
                elif cell == opp:
                    score -= int(10 - (abs(r - cr) + abs(c - cc)))
        return score
