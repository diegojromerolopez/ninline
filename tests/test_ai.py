"""Unit tests for AI recommendations."""

from ninline.ai import AI
from ninline.board import Board, Cell


def test_ai_immediate_win() -> None:
    # X has 2 in a row and can win at (0, 2)
    board = Board.parse("XX.|OO.|...")
    r, c, score = AI.recommend_move(board, win_length=3, player=Cell.X, difficulty="hard")
    assert (r, c) == (0, 2)
    assert score == 100


def test_ai_immediate_block() -> None:
    # Opponent (O) has 2 in a row at row 1, X must block at (1, 2)
    board = Board.parse("X..|OO.|X..")
    r, c, _ = AI.recommend_move(board, win_length=3, player=Cell.X, difficulty="hard")
    assert (r, c) == (1, 2)
