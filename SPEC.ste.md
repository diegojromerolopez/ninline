# ninline Specification

## 1. Product Goal

Build a zero-runtime-dependency Python 3 generalized N-in-a-line game engine.

Support M rows, N columns, and target length K.

Support interactive ANSI play and deterministic JSON command execution.

Use only Python standard-library modules at runtime.

Permit pytest as the development test runner.

## 2. Supported Runtime

Use Python 3.11 or later.

Use strict type annotations.

Run `mypy --strict src/` without errors.

Run `ruff check .` without errors.

Run `ruff format --check .` without changes.

Do not add runtime dependencies.

## 3. Repository Layout

Create these required paths:

- `Makefile`
- `pyproject.toml`
- `README.md`
- `.gitignore`
- `src/ninline/__init__.py`
- `src/ninline/cli.py`
- `src/ninline/board.py`
- `src/ninline/engine.py`
- `src/ninline/ai.py`
- `src/ninline/renderer.py`
- `tests/test_board.py`
- `tests/test_engine.py`
- `tests/test_ai.py`
- `tests/test_cli.py`

Keep the primary executable wrapper thin.

Delegate command execution to a testable function.

Keep each module responsible for one domain capability.

Do not create placeholder functions, `pass`, ellipsis bodies, or `NotImplementedError`.

## 4. Domain Rules

Use a board with M rows and N columns.

Require `3 <= M <= 50`.

Require `3 <= N <= 50`.

Require `3 <= K <= max(M, N)`.

Use `X` for the first player.

Use `O` for the second player.

Use `.` for an empty cell.

Use these statuses: `IN_PROGRESS`, `WIN`, `DRAW`, and `INVALID`.

Count rows from zero.

Count columns from zero.

Count moves as non-empty cells.

Accept only uppercase `X`, `O`, and `.` in board text.

Require rectangular board text.

Require at least one row and one column in parser input.

Reject a board row with zero columns.

Reject a board with invalid symbols.

Reject a board with impossible player counts when the command requires a legal state.

For a legal state, X has either the same count as O or one more mark than O.

Reject a state where both players have winning lines.

Reject a state where the winner has an impossible move count.

Return `INVALID` for an invalid board evaluation.

## 5. Board Serialization

Serialize each row without spaces.

Join rows with `|`.

Serialize an empty cell as `.`.

Serialize the example board as `X.O|.X.|..X`.

Return winning coordinates as `[row, col]` pairs.

Order a winning line from its first scanned cell to its last scanned cell.

Use deterministic scan order: row ascending, column ascending, directions in horizontal, vertical, main-diagonal, anti-diagonal order.

Return one winning line for a winning evaluation.

## 6. Win Detection

Scan these directions:

- Horizontal: `(0, 1)`
- Vertical: `(1, 0)`
- Main diagonal: `(1, 1)`
- Anti-diagonal: `(-1, 1)`

Start a candidate line only when the preceding cell in the same direction is outside the board or has a different mark.

Detect K consecutive equal marks.

Allow a longer line to contain multiple K-length segments.

Return the first deterministic K-length segment.

Return `WIN` and the mark as `winner` after a valid winning line.

Return `DRAW` when the board is full without a winner.

Return `IN_PROGRESS` otherwise.

Set `is_terminal` to true for `WIN`, `DRAW`, and `INVALID`.

Set `is_terminal` to false only for `IN_PROGRESS`.

## 7. CLI Entry Point

Expose an executable named `ninline`.

Support these subcommands:

- `play`
- `eval`
- `move`
- `best-move`
- `info`

Write successful JSON responses to stdout for `eval`, `move`, `best-move`, and `info`.

Write errors to stdout as JSON when a command contract defines an error response.

Write argument parser errors to stderr.

Use exit code `0` for successful computation.

Use exit code `1` for invalid board state or invalid move.

Use exit code `2` for argument parsing or invalid command arguments.

Prefix human-readable stderr errors with `Error: `.

Emit one JSON object per command.

Do not emit logging text on stdout.

## 8. eval Command

Run:

`ninline eval --board BOARD --win-length K`

Parse board dimensions from BOARD.

Return this JSON schema:

```json
{"status":"WIN|DRAW|IN_PROGRESS|INVALID","winner":"X|O|null","winning_line":[[0,0]],"is_terminal":true,"move_count":4,"rows":3,"cols":3,"win_length":3}
```

Return `winning_line` as an empty array when no line exists.

Return `winner` as null when no player wins.

Return exit code `1` for an invalid board state.

## 9. move Command

Run:

`ninline move --board BOARD --win-length K --player X|O --row R --col C`

Reject coordinates outside the board.

Reject an occupied cell.

Reject a player value other than `X` or `O`.

Reject a move on a terminal board.

Return this success schema:

```json
{"success":true,"board":"X.O|.O.|...","status":"IN_PROGRESS","winner":null,"is_terminal":false,"error":null}
```

Return this error schema:

```json
{"success":false,"board":null,"status":"INVALID","winner":null,"is_terminal":true,"error":"<reason>"}
```

Use exit code `1` for occupied, out-of-range, terminal, or invalid-board moves.

## 10. best-move Command

Run:

`ninline best-move --board BOARD --win-length K --player X|O --difficulty easy|hard`

Return this schema:

```json
{"row":0,"col":2,"player":"X","evaluation_score":100}
```

Choose the immediate winning move when one exists.

Block the opponent's immediate winning move when no own win exists.

Use deterministic row-major tie breaking.

Use exact alpha-beta minimax when nine or fewer cells remain open.

Use depth-limited search with maximum depth four on larger boards.

Score wins positively for the requested player.

Score losses negatively for the requested player.

Score center control and weighted patterns for non-terminal positions.

Return exit code `1` when no legal move exists or the board is invalid.

Use integer evaluation scores.

## 11. info Command

Run:

`ninline info --rows M --cols N --win-length K`

Return this schema:

```json
{"rows":6,"cols":7,"win_length":4,"total_cells":42,"total_winning_lines":69,"horizontal_lines":24,"vertical_lines":21,"diagonal_lines":24}
```

Count every distinct K-cell segment in the four directions.

Count horizontal and vertical segments separately.

Count both diagonal directions in `diagonal_lines`.

Return exit code `2` for invalid dimensions or K.

## 12. play Command

Run:

`ninline play --rows M --cols N --win-length K --ai easy|hard --first X|O`

Render the board with ANSI terminal output.

Use a stable box-drawing layout.

Show row and column indexes.

Prompt the human player with `Move (row col): `.

Accept two decimal zero-based integers separated by whitespace.

Reject malformed input without terminating the session.

Reject invalid moves without changing the board.

Show the final result and winning line.

Use the selected AI difficulty.

Use deterministic AI tie breaking.

Exit with code `0` after win or draw.

Exit with code `1` for unrecoverable game errors.

## 13. Build and Quality Commands

Implement these Makefile targets:

- `make build`
- `make test`
- `make lint`
- `make format`
- `make clean`
- `make e2e`

Make `build` validate package imports and the executable entry point.

Make `test` run `pytest -v tests/` and fail when any test fails.

Make `lint` run `ruff check .` and `mypy --strict src/`.

Make `format` run `ruff format --check .`.

Make `clean` remove Python caches, pytest caches, mypy caches, and build artifacts.

Make `e2e` run black-box CLI scenarios for every command and major error path.

Use `docker compose -f docker-compose.e2e.yml up --build --exit-code-from ...` only if containerized E2E testing is added.

Do not use the hyphenated `docker-compose` command.

## 14. Testing Rules

Use Chicago-school tests against real domain objects.

Use in-memory test doubles for external boundaries.

Do not use network services or external databases.

Run black-box CLI tests against the executable.

Assert stdout, stderr, JSON fields, and exit codes.

Cover valid, boundary, malformed, occupied, terminal, and invalid-state inputs.

Use a maximum two-second timeout for each external process interaction.

Do not use static sleep delays for readiness.

Do not use tautological assertions.

Ask whether a script provides a safer method for structured test data.

Require 100 percent test pass rate before release.
