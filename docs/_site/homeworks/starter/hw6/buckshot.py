import random
from dataclasses import dataclass, field

from ai import (
    ALL_ITEMS,
    BEER,
    CIGARETTE,
    HANDCUFFS,
    HANDSAW,
    MAGNIFYING_GLASS,
    SHOOT_OTHER,
    SHOOT_SELF,
)

ITEM_NAMES = {
    HANDSAW: "handsaw",
    MAGNIFYING_GLASS: "magnifying glass",
    CIGARETTE: "cigarette",
    BEER: "beer",
    HANDCUFFS: "handcuffs",
}


@dataclass
class State:
    max_hp: int
    rng: random.Random
    hp: list = field(init=False)
    inventory: list = field(init=False)
    knows_shell: list = field(init=False)
    skip_next: list = field(init=False)
    saw_active: list = field(init=False)
    current_player: int = field(init=False)
    shells: list = field(default_factory=list)
    shell_index: int = 0

    def __post_init__(self):
        self.hp = [self.max_hp, self.max_hp]
        self.inventory = [[0] * 5 for _ in range(2)]
        self.knows_shell = [-1, -1]
        self.skip_next = [False, False]
        self.saw_active = [False, False]
        self.current_player = self.rng.randrange(2)


def remaining_shells(state):
    return state.shells[state.shell_index :]


def reload_shotgun(state):
    total = state.rng.randint(3, 7)
    live = state.rng.randint(1, total - 1)
    state.shells = [1] * live + [0] * (total - live)
    state.rng.shuffle(state.shells)
    state.shell_index = 0
    state.knows_shell = [-1, -1]
    draw_items(state)


def draw_items(state):
    for player in range(2):
        for item in state.rng.sample(ALL_ITEMS, 2):
            if sum(state.inventory[player]) >= 4:
                break
            state.inventory[player][item] += 1


def needs_reload(state):
    remaining = remaining_shells(state)
    return not remaining or 1 not in remaining


def current_shell(state):
    return state.shells[state.shell_index]


def rack_shell(state):
    state.shell_index += 1
    state.knows_shell = [-1, -1]


def observation(state, player):
    other = 1 - player
    remaining = remaining_shells(state)
    info = [
        state.hp[player],
        state.hp[other],
        remaining.count(1),
        remaining.count(0),
        state.knows_shell[player],
        int(state.knows_shell[other] != -1),
        int(state.skip_next[other]),
        int(state.saw_active[player]),
    ]
    info.extend(state.inventory[other])
    info.extend(state.inventory[player])
    assert len(info) == 18
    return info


def legal_actions(state, player):
    actions = [
        item for item in ALL_ITEMS if state.inventory[player][item] > 0
    ]
    return actions + [SHOOT_SELF, SHOOT_OTHER]


def pass_control(state):
    player = state.current_player
    other = 1 - player
    state.saw_active[player] = False
    if state.skip_next[other]:
        state.skip_next[other] = False
    else:
        state.current_player = other


def apply_item(state, player, item):
    state.inventory[player][item] -= 1
    other = 1 - player
    if item == HANDSAW:
        state.saw_active[player] = True
    elif item == MAGNIFYING_GLASS:
        state.knows_shell[player] = current_shell(state)
    elif item == CIGARETTE:
        state.hp[player] = min(state.max_hp, state.hp[player] + 1)
    elif item == BEER:
        rack_shell(state)
    elif item == HANDCUFFS:
        state.skip_next[other] = True


def describe(state):
    remaining = remaining_shells(state)
    return (
        f"P0 HP={state.hp[0]} items={state.inventory[0]} | "
        f"P1 HP={state.hp[1]} items={state.inventory[1]} | "
        f"shells: {remaining.count(1)} live, {remaining.count(0)} blank | "
        f"turn=P{state.current_player}"
    )


def run_game(agent0, agent1, training=False, seed=None, max_hp=7, verbose=False):
    """Run one game and return winner index, decision count, and final state."""
    if seed is not None:
        random.seed(seed)
    state = State(max_hp=max_hp, rng=random.Random(seed))
    agents = [agent0, agent1]
    decisions = 0

    while decisions < 500:
        if needs_reload(state):
            reload_shotgun(state)

        player = state.current_player
        other = 1 - player
        info = observation(state, player)
        action = agents[player].choose_action(info)
        decisions += 1

        if action not in legal_actions(state, player):
            raise ValueError(f"P{player} selected illegal action {action}")

        if action in ALL_ITEMS:
            apply_item(state, player, action)
            agents[player].see_result(
                0, observation(state, player), training
            )
            if verbose:
                print(f"P{player} uses {ITEM_NAMES[action]}")
                print(describe(state))
            continue

        shell = current_shell(state)
        target = player if action == SHOOT_SELF else other
        if verbose:
            target_name = "self" if target == player else f"P{other}"
            shell_name = "live" if shell else "blank"
            print(f"P{player} shoots {target_name}: {shell_name}")

        if shell == 1:
            damage = 2 if state.saw_active[player] else 1
            state.saw_active[player] = False
            state.hp[target] -= damage
        rack_shell(state)

        if state.hp[target] <= 0:
            reward = -1 if target == player else 1
            winner = other if reward == -1 else player
            agents[player].see_result(
                reward, observation(state, player), training
            )
            agents[other].see_result(
                -reward, observation(state, other), training
            )
            if verbose:
                print(describe(state))
                print(f"P{winner} wins")
            return {"winner": winner, "decisions": decisions, "state": state}

        if shell == 1 or target == other:
            pass_control(state)

        agents[player].see_result(0, observation(state, player), training)
        if verbose:
            print(describe(state))

    raise RuntimeError("game exceeded 500 decisions")


if __name__ == "__main__":
    from ai import RandomAgent

    result = run_game(RandomAgent(), RandomAgent(), seed=42, verbose=True)
    print("winner:", result["winner"])
