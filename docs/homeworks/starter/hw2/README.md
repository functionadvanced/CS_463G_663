# Homework 2 starter

This package is a self-contained, console-based Reversi environment. It uses only the Python standard library.

## Files

- `ai.py`: helper functions plus the four functions you must complete.
- `reversi.py`: game rules, board rendering, and a random-vs-random demo.
- `check_ai.py`: public interface and mutation checks.
- `tournament.py`: runs all 16 ordered pairings and saves results.

## First steps

```bash
python reversi.py
python check_ai.py
```

After implementing `ai.py`, run:

```bash
python tournament.py
```

The tournament runner writes `tournament_results.csv` and one representative final board for each ordered pairing in `final_boards/`. These files can be used to build the report tables and screenshots.

Upload only `hw2submission.pdf` to Canvas.
