"""Action-selection policies for the stamina simulation."""

from collections.abc import Callable

from config import ACTIONS, MAX_STAMINA

ActionData = dict[str, int | float]
Actions = dict[str, ActionData]
Strategy = Callable[[int, Actions], str | None]


def conservative_strategy(stamina: int, actions_dict: Actions) -> str | None:
    """Choose normal only when stamina is above 40% of the maximum."""
    if stamina > MAX_STAMINA * 0.4:
        return "normal"
    return None


def aggressive_strategy(stamina: int, actions_dict: Actions) -> str | None:
    """Prefer strong, falling back to normal only when normal is affordable."""
    if stamina >= actions_dict["strong"]["stamina_cost"]:
        return "strong"
    if stamina >= actions_dict["normal"]["stamina_cost"]:
        return "normal"
    return None


def risk_taking_strategy(stamina: int, actions_dict: Actions) -> str | None:
    """Choose risky whenever affordable, then fall back to affordable normal."""
    if stamina >= actions_dict["risky"]["stamina_cost"]:
        return "risky"
    if stamina >= actions_dict["normal"]["stamina_cost"]:
        return "normal"
    return None


def balanced_strategy(stamina: int, actions_dict: Actions) -> str | None:
    """Choose the affordable action with the highest expected value per stamina."""
    affordable = [
        (action_name, action)
        for action_name, action in actions_dict.items()
        if action["stamina_cost"] <= stamina
    ]
    if not affordable:
        return None

    return max(
        affordable,
        key=lambda item: (
            item[1]["reward"] * (1 - item[1]["failure_chance"])
        )
        / item[1]["stamina_cost"],
    )[0]


STRATEGIES: dict[str, Strategy] = {
    "conservative": conservative_strategy,
    "aggressive": aggressive_strategy,
    "risk_taking": risk_taking_strategy,
    "balanced": balanced_strategy,
}