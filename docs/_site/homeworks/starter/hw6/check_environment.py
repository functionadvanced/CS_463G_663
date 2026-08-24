from ai import RandomAgent, legal_action_mask
from buckshot import observation, run_game


def main():
    for seed in range(10):
        result = run_game(RandomAgent(), RandomAgent(), seed=seed)
        assert result["winner"] in (0, 1)
        state = result["state"]
        for player in (0, 1):
            info = observation(state, player)
            assert len(info) == 18
            mask = legal_action_mask(info)
            assert mask.shape == (7,)
            assert bool(mask[5]) and bool(mask[6])
            assert int(mask.sum()) >= 2
    print("Homework 6 environment passed 10 random-agent games.")


if __name__ == "__main__":
    main()
