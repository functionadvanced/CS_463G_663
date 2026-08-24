import random

import numpy as np
import torch
from torch.distributions import Categorical

HANDSAW = 0
MAGNIFYING_GLASS = 1
CIGARETTE = 2
BEER = 3
HANDCUFFS = 4
SHOOT_SELF = 5
SHOOT_OTHER = 6

ALL_ITEMS = [HANDSAW, MAGNIFYING_GLASS, CIGARETTE, BEER, HANDCUFFS]
ALL_ACTIONS = ALL_ITEMS + [SHOOT_SELF, SHOOT_OTHER]
NUM_OBSERVATIONS = 18
NUM_ACTIONS = 7
MY_ITEMS = slice(13, 18)


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def legal_action_mask(info, device=None):
    mask = torch.ones(NUM_ACTIONS, dtype=torch.bool, device=device)
    item_counts = torch.as_tensor(
        info[MY_ITEMS], dtype=torch.float32, device=device
    )
    mask[:5] = item_counts > 0
    return mask


def masked_policy(logits, info):
    mask = legal_action_mask(info, device=logits.device)
    masked_logits = logits.masked_fill(~mask, float("-inf"))
    return Categorical(logits=masked_logits)


class ActorNetwork(torch.nn.Module):
    def __init__(self, input_dim=NUM_OBSERVATIONS, output_dim=NUM_ACTIONS, hidden_dim=128):
        super().__init__()
        # TODO: define a network that returns output_dim logits.
        self.network = None

    def forward(self, info):
        if self.network is None:
            raise NotImplementedError("Define the actor network")
        return self.network(info)


class CriticNetwork(torch.nn.Module):
    def __init__(self, input_dim=NUM_OBSERVATIONS, hidden_dim=128):
        super().__init__()
        # TODO: define a network that returns one scalar value.
        self.network = None

    def forward(self, info):
        if self.network is None:
            raise NotImplementedError("Define the critic network")
        return self.network(info)


class RandomAgent:
    def choose_action(self, info):
        legal = legal_action_mask(info).nonzero().flatten().tolist()
        return random.choice(legal)

    def see_result(self, result, info, training_flag=False):
        pass


class RLAgent:
    def __init__(self):
        # TODO: create networks, optimizers, hyperparameters, and pending state.
        self.actor = None
        self.critic = None

    def train(self, info, result, terminal=False):
        # TODO: perform one Actor-Critic update from the pending transition.
        raise NotImplementedError("Implement RLAgent.train")

    def choose_action(self, info):
        # TODO: sample from a masked policy and store update information.
        raise NotImplementedError("Implement RLAgent.choose_action")

    def see_result(self, result, info, training_flag=False):
        # A nonzero result marks a terminal win (+1) or loss (-1).
        # TODO: update only when training_flag is True and clear terminal state.
        raise NotImplementedError("Implement RLAgent.see_result")
