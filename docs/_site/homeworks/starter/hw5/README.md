# Homework 5 starter

This package contains the complete data pipeline and the interfaces needed for the two-digit MNIST experiment. The CNN architecture and learning loop remain student work.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python check_setup.py
```

The first run downloads MNIST into a local `data/` directory.

## Files

- `hw5_starter.py`: paired dataset, reproducibility helpers, loaders, plotting helper, and TODO interfaces.
- `check_setup.py`: checks imports, data dimensions, labels, and batch construction.
- `requirements.txt`: required Python packages.

Upload only `hw5submission.pdf` to Canvas. Include the complete finished code in the PDF appendix.
