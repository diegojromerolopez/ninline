# ninline Specification: Generalized (M,N,K)-Game CLI and Engine in Python

> **Goal**: Build a high-performance, zero-dependency Python 3 CLI game engine for generalized $N$-in-a-line ($(m,n,k)$-games) on an $M \times N$ grid with target line length $K$. Support interactive ANSI terminal play and deterministic headless JSON subcommands.

---

## ⚡ 1. TL;DR and Core System Invariants

* **Language**: Use Python 3. Use strict type annotations. Verify them with `mypy --strict`. Format the code with `ruff`.
* **Dependencies**: Use only the Python standard library (`argparse`, `json`, `dataclasses`, `enum`, `typing`, `sys`, `random`).
* **Game Rules**:
  * Set grid dimensions to $M$ rows \times $N$ columns ($3 \le M, N \le 50$).
  * Set the target length to $K$ consecutive marks in a straight line to win ($3 \le K \le \max(M, N)$).
  * Use `X` for the First player and `O` for the Second player.
  * Use `X`, `O`, or `.` (empty) for cell states.
  * Use `"IN_PROGRESS"`, `"WIN"`, `"DRAW"`, or `"INVALID"` for game states.

---

## 📁 2. Pinned Directory Layout

```text
ninline/
├── Makefile                 # Build, test, lint, format, and clean commands (REQUIRED)
├── pyproject.toml           # ruff, mypy, and pytest configuration
├── README.md                # Usage and API contract
├── .gitignore               # __pycache__, .pytest_cache, and .mypy_cache
├── src/
│   └── ninline/
│       ├── __init__.py      # Package version and exports
│       ├── cli.py           # CLI dispatch (play, eval, move, best-move, info)
│       ├── board.py         # Board domain model, serialization, and boundary checks
│       ├── engine.py        # Ray-casting line scanner and win/draw evaluator
│       ├── ai.py            # Alpha-Beta Minimax AI and heuristic search
│       └── renderer.py      # ANSI terminal box-drawing board renderer
└── tests/
    ├── test_board.py        # Grid creation, move placement, bounds, and serialization
    ├── test_engine.py       # Ray-casting win detection (H, V, diagonals, and draws)
    ├── test_ai.py           # Immediate win completion and block detection
    └── test_cli.py          # E2E CLI subcommands, JSON schemas, and exit codes
```

---

## 🛠️ 3. Quality and Build Commands (Makefile)

* `make build` → Validate the package structure and the executable entrypoint.
* `make test` → Run all tests with `pytest -v tests/`. Require 100% pass and 0 failures.
* `make lint` → Run `ruff check .` and `mypy --strict src/`. Require 0 warnings and 0 errors.
* `make format` → Run `ruff format --check .`. Require idempotent code formatting.
* `make clean` → Remove `__pycache__`, `.pytest_cache`, and build artifacts.

---

## 🕹️ 4. CLI Subcommand Contracts (Deterministic JSON stdout)

### 4.1 Board Serialization Invariant
* Join rows with `|`.
* Use this example for a $3 \times 3$ grid: `"X.O|.X.|..X"`

### 4.2 `ninline eval` (Evaluate Board State)
```bash
ninline eval --board "X.O|.X.|..X" --win-length 3
```
* **Output Format (stdout)**:
```json
{
  "status": "WIN",
  "winner": "X",
  "winning_line": [[0, 0], [1, 1], [2, 2]],
  "is_terminal": true,
  "move_count": 4,
  "rows": 3,
  "cols": 3,
  "win_length": 3
}
```

### 4.3 `ninline move` (Apply Single Move)
```bash
ninline move --board "X.O|...|..." --win-length 3 --player O --row 1 --col 1
```
* **Output Format (stdout)**:
```json
{
  "success": true,
  "board": "X.O|.O.|...",
  "status": "IN_PROGRESS",
  "winner": null,
  "is_terminal": false,
  "error": null
}
```
* If the move is invalid because the cell is occupied or outside the bounds, exit with `1` and return `{"success": false, "error": "<reason>"}`.

### 4.4 `ninline best-move` (AI Move Recommender)
```bash
ninline best-move --board "XX.|OO.|..." --win-length 3 --player X --difficulty hard
```
* **Output Format (stdout)**:
```json
{
  "row": 0,
  "col": 2,
  "player": "X",
  "evaluation_score": 100
}
```

### 4.5 `ninline info` (Board Metrics)
```bash
ninline info --rows 6 --cols 7 --win-length 4
```
* **Output Format (stdout)**:
```json
{
  "rows": 6,
  "cols": 7,
  "win_length": 4,
  "total_cells": 42,
  "total_winning_lines": 69,
  "horizontal_lines": 24,
  "vertical_lines": 21,
  "diagonal_lines": 24
}
```

### 4.6 `ninline play` (Interactive ANSI Game)
```bash
ninline play --rows 3 --cols 3 --win-length 3 --ai easy --first X
```

---

## 🧠 5. Algorithms and Implementation Details

1. **Ray-Casting Win Scanner (`engine.py`)**:
   * Scan 4 direction vectors from every non-empty cell:
     * Horizontal: `(0, 1)`
     * Vertical: `(1, 0)`
     * Main diagonal: `(1, 1)`
     * Anti-diagonal: `(-1, 1)`
   * Check these bounds: $0 \le r + k \cdot dr < M$ and $0 \le c + k \cdot dc < N$.
2. **AI Decision Engine (`ai.py`)**:
   * Use exact Minimax with Alpha-Beta pruning for boards with $le 9$ open cells.
   * Use depth-limited search ($\text{depth} \le 4$) with weighted pattern scoring for larger boards. Score immediate wins, opponent blocks, and center control.
3. **Exit Codes**:
   * `0`: Normal completion or successful computation.
   * `1`: Invalid move or illegal board state.
   * `2`: CLI argument parse error.
