"""Configuration for the stamina decision simulation."""

ACTIONS = {
    "normal": {"stamina_cost": 5, "reward": 10, "failure_chance": 0.0},
    "strong": {"stamina_cost": 10, "reward": 20, "failure_chance": 0.05},
    "risky": {"stamina_cost": 15, "reward": 35, "failure_chance": 0.3},
}

MAX_STAMINA = 100
STAMINA_LEVELS = {"low": 20, "medium": 50, "high": 100}