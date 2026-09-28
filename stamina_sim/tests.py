"""Assert-based simulation checks; run directly with ``python tests.py``."""

from unittest.mock import patch

from config import ACTIONS, MAX_STAMINA
from simulation import run_simulation, run_turn
from strategies import STRATEGIES


def test_run_turn_keeps_stamina_nonnegative() -> None:
    for stamina in range(MAX_STAMINA + 1):
        for action_name in ACTIONS:
            result = run_turn(stamina, action_name)
            remaining = result.get("stamina_remaining", stamina)
            assert remaining >= 0


def test_strategies_only_choose_affordable_actions() -> None:
    low_stamina = 4
    for strategy in STRATEGIES.values():
        action_name = strategy(low_stamina, ACTIONS)
        assert action_name is None or ACTIONS[action_name]["stamina_cost"] <= low_stamina


def test_failed_actions_award_no_points() -> None:
    with patch("simulation.random.random", return_value=0.0):
        result = run_turn(10, "strong")
    assert result["success"] is False
    assert result["points_earned"] == 0


def test_simulation_log_matches_turn_count_or_early_end() -> None:
    def choose_normal(
        stamina: int, actions_dict: dict[str, dict[str, int | float]]
    ) -> str:
        return "normal"

    num_turns = 4
    with patch("simulation.random.random", return_value=0.5):
        result = run_simulation(choose_normal, 5, num_turns)
    log = result["log"]
    assert isinstance(log, list)
    assert len(log) == num_turns or (
        result["final_stamina"] == 0 and len(log) < num_turns
    )


def test_each_strategy_runs_at_all_stamina_levels() -> None:
    for strategy in STRATEGIES.values():
        for stamina in (0, 20, 50, 100):
            result = run_simulation(strategy, stamina, 3)
            assert isinstance(result["log"], list)
            assert len(result["log"]) == 3


def main() -> None:
    tests = [
        ("run_turn keeps stamina nonnegative", test_run_turn_keeps_stamina_nonnegative),
        ("strategies choose affordable actions", test_strategies_only_choose_affordable_actions),
        ("failed actions award zero points", test_failed_actions_award_no_points),
        ("simulation log length is valid", test_simulation_log_matches_turn_count_or_early_end),
        ("all strategies run at each stamina level", test_each_strategy_runs_at_all_stamina_levels),
    ]
    failures = []

    for test_name, test_function in tests:
        try:
            test_function()
        except Exception as error:
            print(f"FAIL: {test_name} ({type(error).__name__}: {error})")
            failures.append(test_name)
        else:
            print(f"PASS: {test_name}")

    if failures:
        print("FAILED TESTS: " + ", ".join(failures))
    else:
        print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()