import random
from unittest.mock import patch

from ai import HANDCUFFS, HANDSAW, SHOOT_OTHER, SHOOT_SELF
from ai import RandomAgent, legal_action_mask
from buckshot import State, observation, run_game


class ScriptedAgent:
    def __init__(self, actions):
        self.actions = iter(actions)
        self.observations = []

    def choose_action(self, info):
        self.observations.append(info)
        return next(self.actions)

    def see_result(self, result, info, training_flag=False):
        pass


def scripted_game(shells, hp, actions0, actions1):
    state = State(max_hp=7, rng=random.Random(0))
    state.current_player = 0
    state.hp = list(hp)
    state.shells = shells
    state.inventory[0][HANDSAW] = 1
    state.inventory[0][HANDCUFFS] = 1
    first, second = ScriptedAgent(actions0), ScriptedAgent(actions1)
    with patch("buckshot.State", return_value=state):
        result = run_game(first, second, seed=0)
    return result, first


def main():
    # A live shot is doubled, whether aimed at self or opponent.
    for target, expected_winner in ((SHOOT_SELF, 1), (SHOOT_OTHER, 0)):
        result, _ = scripted_game([1, 0], (2, 2), [HANDSAW, target], [])
        assert result["winner"] == expected_winner
        assert result["decisions"] == 2
        assert not any(result["state"].saw_active)

    # A blank self-shot keeps control but consumes the handsaw bonus.
    result, first = scripted_game(
        [0, 1, 1], (1, 2), [HANDSAW, SHOOT_SELF, SHOOT_OTHER], [SHOOT_OTHER]
    )
    assert first.observations[1][7] == 1  # Bonus exists before the blank.
    assert first.observations[2][7] == 0  # Gone on the retained turn.
    assert result["winner"] == 1  # The following live shot dealt only one.

    # Handcuffs also retain control without preserving the bonus after a blank.
    result, first = scripted_game(
        [0, 1, 1], (1, 2),
        [HANDSAW, HANDCUFFS, SHOOT_OTHER, SHOOT_OTHER], [SHOOT_OTHER]
    )
    assert first.observations[2][7] == 1
    assert first.observations[3][7] == 0
    assert result["winner"] == 1

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
    print("Homework 6 environment passed handsaw checks and 10 random-agent games.")


if __name__ == "__main__":
    main()
