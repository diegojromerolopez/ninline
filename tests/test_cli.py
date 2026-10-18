"""End-to-end CLI tests."""

import json
import pytest
from ninline.cli import run_app


def test_cli_eval(capsys: pytest.CaptureFixture[str]) -> None:
    code = run_app(["eval", "--board", "X.O|.X.|..X", "--win-length", "3"])
    assert code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["status"] == "WIN"
    assert data["winner"] == "X"
    assert data["winning_line"] == [[0, 0], [1, 1], [2, 2]]
    assert data["move_count"] == 4


def test_cli_move_success(capsys: pytest.CaptureFixture[str]) -> None:
    code = run_app([
        "move", "--board", "X.O|...|...", "--win-length", "3",
        "--player", "O", "--row", "1", "--col", "1",
    ])
    assert code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["success"] is True
    assert data["board"] == "X.O|.O.|..."
    assert data["status"] == "IN_PROGRESS"


def test_cli_move_occupied(capsys: pytest.CaptureFixture[str]) -> None:
    code = run_app([
        "move", "--board", "X.O|...|...", "--win-length", "3",
        "--player", "X", "--row", "0", "--col", "0",
    ])
    assert code == 1
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["success"] is False
    assert "occupied" in data["error"]


def test_cli_info(capsys: pytest.CaptureFixture[str]) -> None:
    code = run_app(["info", "--rows", "6", "--cols", "7", "--win-length", "4"])
    assert code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["total_winning_lines"] == 69
    assert data["horizontal_lines"] == 24


def test_cli_best_move(capsys: pytest.CaptureFixture[str]) -> None:
    code = run_app([
        "best-move", "--board", "XX.|OO.|...", "--win-length", "3",
        "--player", "X", "--difficulty", "hard",
    ])
    assert code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["row"] == 0
    assert data["col"] == 2
    assert data["player"] == "X"
