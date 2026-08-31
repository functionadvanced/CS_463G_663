"""Lecture 2b: compare reflex and memory-based vacuum agents.

Run with Python 3. No packages or imports are required.
True means dirty; False means clean; None means unknown to the agent.
"""


class VacuumWorld:
    def __init__(self, start="A", dirt=None):
        self.position = start
        self.dirt = {"A": True, "B": True} if dirt is None else dict(dirt)

    def perceive(self):
        room = self.position
        return room, self.dirt[room]

    def apply(self, action):
        if action == "Suck":
            self.dirt[self.position] = False
        elif action == "Left":
            self.position = "A"
        elif action == "Right":
            self.position = "B"
        elif action != "NoOp":
            raise ValueError(f"Unknown action: {action}")


class ReflexAgent:
    def act(self, percept):
        room, dirty = percept
        if dirty:
            return "Suck"
        return "Right" if room == "A" else "Left"


class MemoryAgent:
    def __init__(self):
        self.seen = {"A": None, "B": None}

    def act(self, percept):
        room, dirty = percept
        self.seen[room] = dirty
        if dirty:
            self.seen[room] = False  # Predict a successful cleaning action.
            return "Suck"
        if all(value is False for value in self.seen.values()):
            return "NoOp"
        return "Right" if room == "A" else "Left"


def run_agent(agent, start="A", dirt=None, steps=8, redirty_at=None):
    world = VacuumWorld(start, dirt)
    trace, score = [], 0.0
    for step in range(1, steps + 1):
        if step == redirty_at:
            world.dirt["A"] = True
        percept = world.perceive()
        action = agent.act(percept)
        world.apply(action)
        clean = sum(not value for value in world.dirt.values())
        effort = int(action != "NoOp")
        score += clean - 0.25 * effort
        trace.append((step, percept, action, clean, effort))
    return trace, score


def show_comparison(redirty_at=None):
    reflex_trace, reflex_score = run_agent(ReflexAgent(), redirty_at=redirty_at)
    memory_trace, memory_score = run_agent(MemoryAgent(), redirty_at=redirty_at)
    if redirty_at is None:
        label = "No new dirt"
    else:
        label = f"Room A becomes dirty at step {redirty_at}"
    print(f"\n{label}")
    print(
        "Step | Reflex action | Memory action | "
        "Clean rooms (reflex / memory)"
    )
    for reflex, memory in zip(reflex_trace, memory_trace):
        row = (
            f"{reflex[0]:4} | {reflex[2]:13} | "
            f"{memory[2]:13} | {reflex[3]} / {memory[3]}"
        )
        print(row)
    print(f"Scores: reflex={reflex_score:.2f}, memory={memory_score:.2f}")
    print("Non-idle actions:", sum(row[4] for row in reflex_trace), "/",
          sum(row[4] for row in memory_trace))


def self_check():
    cases = 0
    for start in ("A", "B"):
        for dirty_a in (False, True):
            for dirty_b in (False, True):
                dirt = {"A": dirty_a, "B": dirty_b}
                reflex_trace, reflex_score = run_agent(
                    ReflexAgent(), start, dirt
                )
                memory_trace, memory_score = run_agent(
                    MemoryAgent(), start, dirt
                )
                assert reflex_trace[-1][3] == memory_trace[-1][3] == 2
                assert memory_trace[-1][2] == "NoOp"
                assert memory_score >= reflex_score
                assert dirt == {"A": dirty_a, "B": dirty_b}
                cases += 1
    assert run_agent(ReflexAgent())[1] == 12.0
    assert run_agent(MemoryAgent())[1] == 13.25
    assert run_agent(ReflexAgent(), redirty_at=5)[1] == 12.0
    assert run_agent(MemoryAgent(), redirty_at=5)[1] == 9.25
    assert MemoryAgent().act(("A", False)) == "Right"
    print(
        f"Checks passed: {cases} starting worlds, "
        "baseline scores, and new-dirt case."
    )


if __name__ == "__main__":
    self_check()
    show_comparison()
    show_comparison(redirty_at=5)
