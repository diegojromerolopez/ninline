"""Unit tests for Board domain model."""

import pytest
from ninline.board import Board, Cell


def test_board_creation() -> None:
    board = Board.create(3, 3)
    assert board.rows == 3
    assert board.cols == 3
    assert board.count_moves() == 0
    assert len(board.get_empty_cells()) == 9


def test_board_serialization() -> None:
    serialized = "X.O|.X.|..X"
    board = Board.parse(serialized)
    assert board.rows == 3
    assert board.cols == 3
    assert board.get(0, 0) == Cell.X
    assert board.get(0, 1) == Cell.EMPTY
    assert board.get(0, 2) == Cell.O
    assert board.serialize() == serialized


def test_board_bounds() -> None:
    board = Board.create(4, 5)
    assert board.is_in_bounds(0, 0)
    assert board.is_in_bounds(3, 4)
    assert not board.is_in_bounds(4, 4)
    assert not board.is_in_bounds(-1, 0)

    with pytest.raises(IndexError):
        board.get(4, 0)
