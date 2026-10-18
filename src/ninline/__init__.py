"""ninline package initialization."""

from .board import Board, Cell, GameStatus
from .engine import EvaluationResult, Evaluator

__version__ = "0.1.0"
__all__ = ["Board", "Cell", "GameStatus", "Evaluator", "EvaluationResult"]
