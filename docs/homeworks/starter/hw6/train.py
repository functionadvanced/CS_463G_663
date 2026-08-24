import csv

import matplotlib.pyplot as plt

from ai import RLAgent, RandomAgent, set_seed
from buckshot import run_game

TRAINING_GAMES = 1_000
CHECKPOINT_EVERY = 100
EVALUATION_GAMES = 200
BASE_SEED = 42


def evaluate(agent, games=EVALUATION_GAMES, seed_offset=100_000):
    wins = 0
    for game in range(games):
        baseline = RandomAgent()
        seed = seed_offset + game
        if game % 2 == 0:
            result = run_game(agent, baseline, training=False, seed=seed)
            wins += result["winner"] == 0
        else:
            result = run_game(baseline, agent, training=False, seed=seed)
            wins += result["winner"] == 1
    return wins / games


def save_history(history):
    with open("learning_curve.csv", "w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["training_games", "winning_rate"])
        writer.writerows(history)

    x_values = [row[0] for row in history]
    y_values = [row[1] for row in history]
    plt.figure(figsize=(7, 4))
    plt.plot(x_values, y_values, marker="o")
    plt.xlabel("Training games")
    plt.ylabel("Winning rate vs. random agent")
    plt.ylim(0, 1)
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig("learning_curve.png", dpi=180)


def main():
    set_seed(BASE_SEED)
    learner = RLAgent()
    history = [(0, evaluate(learner, seed_offset=200_000))]

    for game in range(1, TRAINING_GAMES + 1):
        opponent = RandomAgent()
        if game % 2 == 0:
            run_game(learner, opponent, training=True, seed=BASE_SEED + game)
        else:
            run_game(opponent, learner, training=True, seed=BASE_SEED + game)

        if game % CHECKPOINT_EVERY == 0:
            rate = evaluate(learner, seed_offset=200_000 + game)
            history.append((game, rate))
            print(f"checkpoint {game}: winning rate {rate:.3f}")

    save_history(history)
    print("wrote learning_curve.csv and learning_curve.png")


if __name__ == "__main__":
    main()
