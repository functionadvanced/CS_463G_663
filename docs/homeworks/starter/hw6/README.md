# Homework 6 starter

This package contains the complete Buckshot environment and the interfaces needed for an Actor-Critic agent. The actor, critic, and update rule remain student work.

## Setup

```bash
python -m pip install -r requirements.txt
python check_environment.py
```

## Play the game

Run `python main.py` to open the PySide6 game. In Settings, choose Human or Random for each player. Choose Actor-Critic after completing the agent and running `python train.py` in this folder. Use **Game → New Game** to restart or change players.

Health appears as green segments above each player. The shotgun rests beside the current player, whose name has a gold outline. Items are dealt one at a time into each player's tray. Click an item in the active player's tray to use it, or hover over it to read its effect. Each copy has its own icon and moves from the tray to where it is used. On your turn, click either player's portrait to shoot that player.

The table shows the remaining live and blank shells together in one tray, grouped by type. The shooter reaches for the shotgun and turns it toward the selected player. A live hit flashes the target, shows the damage, and drains health one segment at a time. Each item has its own animation. Cuffs stay on the affected player's wrists until their turn is skipped, and the barrel stays short until the player fires. The move log records each action and its public outcome. If two people share the screen, the other player should look away when a magnifying glass reveals a shell.

The **About** button shows the credits and the educational-use note.

## Files

- `ai.py`: action constants, mask helper, random baseline, and unfinished Actor-Critic classes.
- `main.py`: launches the PySide6 game and player settings.
- `table_widget.py`: draws the illustrated table, interactive portraits, and action effects.
- `buckshot.py`: complete game rules and an 18-value observation interface.
- `train.py`: headless training, evaluation, learning-curve output, and final weights.
- `check_environment.py`: random-agent smoke tests and observation/mask checks.
- `requirements.txt`: required Python packages.

## Train and try your agent

Implement `ActorNetwork`, `CriticNetwork`, and `RLAgent` in `ai.py`. Keep the networks on `self.actor` and `self.critic`, and only update the agent when `training_flag` is true.

Run `python train.py`. It writes `learning_curve.csv`, `learning_curve.png`, and the final network weights in `agent.pt`. Run `python main.py` from the same folder and select Actor-Critic to play with those weights. Use the headless evaluation results for your report.

Upload only `hw6submission.pdf` to Canvas. Include only your `ai.py` and any other source files you wrote or modified in the PDF appendix.
