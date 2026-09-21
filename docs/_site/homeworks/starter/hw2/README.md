# Homework 2 starter

This is the PySide6 Reversi game from Spring 2025 Homework 2.

## First steps

Install PySide6, then run the game from this folder:

```bash
python -m pip install PySide6
python main.py
```

The settings window lets you choose a human or AI player for each side. You can use human and random players before completing the assignment.

## Files

- `ai.py`: the original unfinished AI starter, with `utility`, `greedy_ai`, `minimax_ai`, and `alpha_beta_ai` to complete.
- `main.py`: launches the PySide6 application.
- `main_window.py`: connects the game, player settings, and AI agents.
- `setting_window.py`: player selection window.
- `board_widget.py`: board drawing, mouse input, and piece animations.
- `info_widget.py`: score and move history display.
- `game_logic.py`: Reversi game rules.

Complete the four functions in `ai.py` before selecting their corresponding AI players. Follow the Homework 2 assignment for the experiments and report requirements.
