# Homework 6 starter

This package contains the complete Buckshot environment and the interfaces needed for an Actor-Critic agent. The actor, critic, and update rule remain student work.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python check_environment.py
```

## Files

- `ai.py`: action constants, mask helper, random baseline, and unfinished Actor-Critic classes.
- `buckshot.py`: complete game rules and an 18-value observation interface.
- `train.py`: reproducible training/checkpoint/evaluation harness and learning-curve output.
- `check_environment.py`: random-agent smoke tests and observation/mask checks.
- `requirements.txt`: required Python packages.

After implementing `RLAgent` in `ai.py`, run `python train.py`. It writes `learning_curve.csv` and `learning_curve.png`.

Upload only `hw6submission.pdf` to Canvas. Include all finished source code in the PDF appendix.
