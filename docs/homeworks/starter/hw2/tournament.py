import csv
import random
from pathlib import Path

from ai import alpha_beta_ai, greedy_ai, minimax_ai, random_ai
from reversi import render_board, run_game

SEARCH_DEPTH = 3
TRIALS_PER_PAIRING = 10
RANDOM_SEED = 42


def minimax_player(board, player):
    return minimax_ai(board, player, SEARCH_DEPTH)


def alpha_beta_player(board, player):
    return alpha_beta_ai(board, player, SEARCH_DEPTH)


AGENTS = {
    "random": random_ai,
    "greedy": greedy_ai,
    "minimax": minimax_player,
    "alpha_beta": alpha_beta_player,
}


def run_tournament():
    random.seed(RANDOM_SEED)
    rows = []
    board_dir = Path("final_boards")
    board_dir.mkdir(exist_ok=True)

    for black_name, black_agent in AGENTS.items():
        for white_name, white_agent in AGENTS.items():
            black_wins = white_wins = ties = 0
            black_total = white_total = 0
            representative = None

            for _ in range(TRIALS_PER_PAIRING):
                result = run_game(black_agent, white_agent)
                representative = result
                black_total += result["black"]
                white_total += result["white"]
                if result["winner"] == "black":
                    black_wins += 1
                elif result["winner"] == "white":
                    white_wins += 1
                else:
                    ties += 1

            board_path = board_dir / f"{black_name}_vs_{white_name}.txt"
            board_path.write_text(render_board(representative["board"]) + "\n")
            rows.append(
                {
                    "black_agent": black_name,
                    "white_agent": white_name,
                    "trials": TRIALS_PER_PAIRING,
                    "black_wins": black_wins,
                    "white_wins": white_wins,
                    "ties": ties,
                    "mean_black_discs": black_total / TRIALS_PER_PAIRING,
                    "mean_white_discs": white_total / TRIALS_PER_PAIRING,
                    "representative_board": str(board_path),
                }
            )

    with open("tournament_results.csv", "w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(
            f"{row['black_agent']:>10} vs {row['white_agent']:<10} "
            f"W-L-T {row['black_wins']}-{row['white_wins']}-{row['ties']}"
        )
    print("wrote tournament_results.csv and final_boards/")


if __name__ == "__main__":
    run_tournament()
