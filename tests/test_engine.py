"""Unit tests for line evaluation and win/draw detection."""

from ninline.board import Board, GameStatus
from ninline.engine import Evaluator


def test_eval_in_progress() -> None:
    board = Board.parse("X.O|...|...")
    res = Evaluator.evaluate(board, 3)
    assert res.status == GameStatus.IN_PROGRESS
    assert not res.is_terminal
    assert res.winner is None


def test_eval_diagonal_win() -> None:
    board = Board.parse("X.O|.X.|..X")
    res = Evaluator.evaluate(board, 3)
    assert res.status == GameStatus.WIN
    assert res.winner == "X"
    assert res.winning_line == [(0, 0), (1, 1), (2, 2)]
    assert res.is_terminal


def test_eval_horizontal_win() -> None:
    board = Board.parse("XXX|OO.|...")
    res = Evaluator.evaluate(board, 3)
    assert res.status == GameStatus.WIN
    assert res.winner == "X"
    assert res.winning_line == [(0, 0), (0, 1), (0, 2)]


def test_eval_draw() -> None:
    board = Board.parse("XOX|XXO|OXO")
    res = Evaluator.evaluate(board, 3)
    assert res.status == GameStatus.DRAW
    assert res.is_terminal
    assert res.winner is None


def test_eval_info_lines() -> None:
    info = Evaluator.count_winning_lines(6, 7, 4)
    assert info["rows"] == 6
    assert info["cols"] == 7
    assert info["win_length"] == 4
    assert info["total_cells"] == 42
    assert info["horizontal_lines"] == 24
    assert info["vertical_lines"] == 21
    assert info["diagonal_lines"] == 24
    assert info["total_winning_lines"] == 69
