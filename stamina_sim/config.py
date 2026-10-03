"""Configuration for the stamina decision simulation."""

ACTIONS = {
    "normal": {"stamina_cost": 5, "reward": 10, "failure_chance": 0.0},
    "strong": {"stamina_cost": 10, "reward": 20, "failure_chance": 0.05},
    "risky": {"stamina_cost": 15, "reward": 35, "failure_chance": 0.3},
}

DIFFICULTY_LEVELS = {
    "easy": {"failure_multiplier": 0.5, "cost_multiplier": 1.0},
    "medium": {"failure_multiplier": 1.0, "cost_multiplier": 1.0},
    "hard": {"failure_multiplier": 1.75, "cost_multiplier": 1.2},
}


def get_actions_for_difficulty(difficulty_name):
    difficulty = DIFFICULTY_LEVELS[difficulty_name]

    return {
        action_name: {
            **action,
            "failure_chance": min(
                1.0, action["failure_chance"] * difficulty["failure_multiplier"]
            ),
            "stamina_cost": max(
                1, round(action["stamina_cost"] * difficulty["cost_multiplier"])
            ),
        }
        for action_name, action in ACTIONS.items()
    }

MAX_STAMINA = 100
STAMINA_LEVELS = {"low": 20, "medium": 50, "high": 100}
