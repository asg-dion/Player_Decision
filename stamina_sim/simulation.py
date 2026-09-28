"""Turn and game-loop logic for stamina-based action selection."""

import random
from collections.abc import Callable

from config import ACTIONS, MAX_STAMINA

ActionData = dict[str, int | float]
Actions = dict[str, ActionData]
Strategy = Callable[[int, Actions], str | None]
TurnResult = dict[str, int | str | bool]
SimulationStrategy = Callable[[int, Actions], str | None]


def run_turn(stamina: int, action_name: str | None) -> TurnResult:
    """Resolve one selected action, or record a skipped turn."""
    if action_name is None:
        return {"skipped": True}

    action = ACTIONS[action_name]
    stamina_cost = int(action["stamina_cost"])
    if stamina < stamina_cost:
        return {"skipped": True}

    success = random.random() >= float(action["failure_chance"])
    return {
        "stamina_remaining": stamina - stamina_cost,
        "action_taken": action_name,
        "success": success,
        "points_earned": int(action["reward"]) if success else 0,
    }


def run_simulation(
    strategy_function: SimulationStrategy,
    starting_stamina: int,
    num_turns: int,
) -> dict[str, int | list[TurnResult]]:
    """Run a fixed number of turns and collect score and action outcomes.

    Skipped turns are included in the log and ``turns_completed`` count, but
    are excluded from the success and failure counts.
    """
    current_stamina = starting_stamina
    total_score = 0
    successes = 0
    failures = 0
    log: list[TurnResult] = []

    for _ in range(num_turns):
        action_name = strategy_function(current_stamina, ACTIONS)
        result = run_turn(current_stamina, action_name)
        log.append(result)

        if result.get("skipped"):
            continue

        current_stamina = int(result["stamina_remaining"])
        total_score += int(result["points_earned"])
        if result["success"]:
            successes += 1
        else:
            failures += 1

    return {
        "log": log,
        "final_stamina": current_stamina,
        "total_score": total_score,
        "turns_completed": len(log),
        "successes": successes,
        "failures": failures,
    }


def play_turn(
    stamina: int, strategy: Strategy, rng: random.Random
) -> tuple[int, int, str | None]:
    """Play one turn, returning remaining stamina, reward, and action name."""
    action_name = strategy(stamina, ACTIONS)
    if action_name is None:
        return stamina, 0, None
    if action_name not in ACTIONS:
        raise ValueError(f"Unknown action: {action_name}")

    action = ACTIONS[action_name]
    if action["stamina_cost"] > stamina:
        return stamina, 0, None

    reward = 0
    if rng.random() >= action["failure_chance"]:
        reward = action["reward"]
    return stamina - action["stamina_cost"], reward, action_name


def simulate_game(
    strategy: Strategy, initial_stamina: int, rng: random.Random | None = None
) -> dict[str, int]:
    """Run one game until the strategy cannot choose an affordable action."""
    if not 0 <= initial_stamina <= MAX_STAMINA:
        raise ValueError(f"initial_stamina must be between 0 and {MAX_STAMINA}")

    game_rng = rng if rng is not None else random.Random()
    stamina = initial_stamina
    total_reward = 0
    action_count = 0
    successful_actions = 0

    while True:
        stamina, reward, action_name = play_turn(stamina, strategy, game_rng)
        if action_name is None:
            break
        action_count += 1
        total_reward += reward
        successful_actions += reward > 0

    return {
        "total_reward": total_reward,
        "action_count": action_count,
        "successful_actions": successful_actions,
        "remaining_stamina": stamina,
    }