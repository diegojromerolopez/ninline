# ninline

Generalized $(M,N,K)$-Game CLI and Engine in pure Python 3 with zero external runtime dependencies.

## Usage

```bash
# Evaluate board state
ninline eval --board "X.O|.X.|..X" --win-length 3

# Make a move
ninline move --board "X.O|...|..." --win-length 3 --player O --row 1 --col 1

# Best move (AI recommendation)
ninline best-move --board "XX.|OO.|..." --win-length 3 --player X --difficulty hard

# Board metric information
ninline info --rows 6 --cols 7 --win-length 4

# Interactive ANSI play
ninline play --rows 3 --cols 3 --win-length 3 --ai easy --first X
```
