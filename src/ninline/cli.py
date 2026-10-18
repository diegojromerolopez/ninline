"""CLI dispatch module for ninline."""

from __future__ import annotations

import argparse
import json
import sys
from typing import NoReturn, Optional, Sequence

from .ai import AI
from .board import Board, Cell, GameStatus
from .engine import Evaluator
from .renderer import Renderer


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        sys.stderr.write(f"error: {message}\n")
        sys.exit(2)


def build_parser() -> argparse.ArgumentParser:
    parser = CustomArgumentParser(
        prog="ninline",
        description="Generalized (M,N,K)-Game CLI and Engine",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # eval subcommand
    eval_parser = subparsers.add_parser("eval", help="Evaluate board state")
    eval_parser.add_argument("--board", required=True, type=str, help="Board serialized string (e.g. 'X.O|.X.|..X')")
    eval_parser.add_argument("--win-length", required=True, type=int, help="Winning line target length K")

    # move subcommand
    move_parser = subparsers.add_parser("move", help="Apply single move to board")
    move_parser.add_argument("--board", required=True, type=str, help="Board serialized string")
    move_parser.add_argument("--win-length", required=True, type=int, help="Winning line target length K")
    move_parser.add_argument("--player", required=True, choices=["X", "O"], help="Player to move (X or O)")
    move_parser.add_argument("--row", required=True, type=int, help="Target row index")
    move_parser.add_argument("--col", required=True, type=int, help="Target col index")

    # best-move subcommand
    bm_parser = subparsers.add_parser("best-move", help="AI Move Recommender")
    bm_parser.add_argument("--board", required=True, type=str, help="Board serialized string")
    bm_parser.add_argument("--win-length", required=True, type=int, help="Winning line target length K")
    bm_parser.add_argument("--player", required=True, choices=["X", "O"], help="Player to move (X or O)")
    bm_parser.add_argument("--difficulty", choices=["easy", "hard"], default="hard", help="AI difficulty level")

    # info subcommand
    info_parser = subparsers.add_parser("info", help="Board Metrics and winning lines count")
    info_parser.add_argument("--rows", required=True, type=int, help="Row count M")
    info_parser.add_argument("--cols", required=True, type=int, help="Col count N")
    info_parser.add_argument("--win-length", required=True, type=int, help="Target line length K")

    # play subcommand
    play_parser = subparsers.add_parser("play", help="Interactive ANSI Game")
    play_parser.add_argument("--rows", type=int, default=3, help="Row count M")
    play_parser.add_argument("--cols", type=int, default=3, help="Col count N")
    play_parser.add_argument("--win-length", type=int, default=3, help="Target line length K")
    play_parser.add_argument("--ai", choices=["easy", "hard"], default="easy", help="AI difficulty")
    play_parser.add_argument("--first", choices=["X", "O"], default="X", help="First player")

    return parser


def handle_eval(args: argparse.Namespace) -> int:
    try:
        board = Board.parse(args.board)
        res = Evaluator.evaluate(board, args.win_length)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1
    print(json.dumps(res.to_dict()))
    return 0


def handle_move(args: argparse.Namespace) -> int:
    try:
        board = Board.parse(args.board)
        Evaluator.validate_win_length(board.rows, board.cols, args.win_length)
        if not board.is_in_bounds(args.row, args.col):
            out = {
                "success": False,
                "board": args.board,
                "status": GameStatus.INVALID.value,
                "winner": None,
                "is_terminal": True,
                "error": f"Move ({args.row}, {args.col}) out of bounds",
            }
            print(json.dumps(out))
            return 1
        if not board.is_empty(args.row, args.col):
            out = {
                "success": False,
                "board": args.board,
                "status": GameStatus.INVALID.value,
                "winner": None,
                "is_terminal": True,
                "error": f"Cell ({args.row}, {args.col}) already occupied",
            }
            print(json.dumps(out))
            return 1

        player_cell = Cell(args.player)
        board.set(args.row, args.col, player_cell)
        res = Evaluator.evaluate(board, args.win_length)
        out = {
            "success": True,
            "board": board.serialize(),
            "status": res.status.value,
            "winner": res.winner,
            "is_terminal": res.is_terminal,
            "error": None,
        }
        print(json.dumps(out))
        return 0
    except Exception as e:
        out = {
            "success": False,
            "board": args.board,
            "status": GameStatus.INVALID.value,
            "winner": None,
            "is_terminal": True,
            "error": str(e),
        }
        print(json.dumps(out))
        return 1


def handle_best_move(args: argparse.Namespace) -> int:
    try:
        board = Board.parse(args.board)
        Evaluator.validate_win_length(board.rows, board.cols, args.win_length)
        player = Cell(args.player)
        row, col, score = AI.recommend_move(board, args.win_length, player, args.difficulty)
        out = {
            "row": row,
            "col": col,
            "player": player.value,
            "evaluation_score": score,
        }
        print(json.dumps(out))
        return 0
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


def handle_info(args: argparse.Namespace) -> int:
    try:
        metrics = Evaluator.count_winning_lines(args.rows, args.cols, args.win_length)
        print(json.dumps(metrics))
        return 0
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


def handle_play(args: argparse.Namespace) -> int:
    board = Board.create(args.rows, args.cols)
    current_turn = Cell(args.first)
    human_cell = Cell.X
    ai_cell = Cell.O

    print(f"Starting ({args.rows},{args.cols},{args.win_length})-Game against AI ({args.ai})!")
    print(Renderer.render(board))

    while True:
        res = Evaluator.evaluate(board, args.win_length)
        if res.is_terminal:
            print(Renderer.render(board, winning_line=res.winning_line))
            if res.status == GameStatus.WIN:
                print(f"Game Over! Winner: {res.winner}")
            else:
                print("Game Over! Draw.")
            break

        if current_turn == human_cell:
            print(f"Your move ({human_cell.value}). Format: row col")
            try:
                line = input("> ").strip()
                if not line:
                    continue
                parts = line.split()
                r, c = int(parts[0]), int(parts[1])
                if not board.is_in_bounds(r, c) or not board.is_empty(r, c):
                    print("Invalid move. Cell occupied or out of bounds.")
                    continue
                board.set(r, c, human_cell)
                current_turn = ai_cell
            except (EOFError, KeyboardInterrupt):
                print("\nGame aborted.")
                return 0
            except Exception:
                print("Invalid input format. Use: row col")
                continue
        else:
            print(f"AI ({ai_cell.value}) is thinking...")
            r, c, _ = AI.recommend_move(board, args.win_length, ai_cell, difficulty=args.ai)
            board.set(r, c, ai_cell)
            print(f"AI played: {r} {c}")
            current_turn = human_cell

        print(Renderer.render(board))
    return 0


def run_app(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.subcommand == "eval":
        return handle_eval(args)
    elif args.subcommand == "move":
        return handle_move(args)
    elif args.subcommand == "best-move":
        return handle_best_move(args)
    elif args.subcommand == "info":
        return handle_info(args)
    elif args.subcommand == "play":
        return handle_play(args)
    return 0


def main() -> None:
    sys.exit(run_app())


if __name__ == "__main__":
    main()
