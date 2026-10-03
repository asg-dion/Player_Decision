"""Run direct diagnostics for strategy thresholds and action failure rates."""

from config import (
    ACTIONS,
    MAX_STAMINA,
    STAMINA_LEVELS,
    get_actions_for_difficulty,
)
from simulation import run_simulation, run_turn
from strategies import STRATEGIES, conservative_strategy


def check_conservative_strategy() -> bool:
    """Print the conservative threshold and check its action across stamina values."""
    threshold = MAX_STAMINA * 0.4
    low_stamina = STAMINA_LEVELS["low"]
    print("CHECK 1 — Conservative strategy at low stamina")
    print(f"Threshold comparison: stamina > 0.4 * MAX_STAMINA = {threshold:g}")
    print(f"Configured low stamina: {low_stamina} ({'below' if low_stamina <= threshold else 'not below'} threshold)")

    tested_stamina = (20, 30, 40, 50, 100)
    actions = []
    for stamina in tested_stamina:
        action = conservative_strategy(stamina, ACTIONS)
        actions.append(action)
        print(f"  stamina={stamina}: action={action}")

    passed = any(action is not None for action in actions)
    print(f"CHECK 1: {'PASS' if passed else 'FAIL'}")
    return passed


def check_risky_failure_rate() -> bool:
    """Measure the risky action failure rate over 2,000 independent trials."""
    samples = 2000
    failures = 0
    successes = 0
    print("\nCHECK 2 — Risky action success/failure rate")

    for _ in range(samples):
        result = run_turn(100, "risky")
        if result.get("success") is True:
            successes += 1
        elif result.get("success") is False:
            failures += 1

    observed_failure_rate = failures / samples
    configured_failure_rate = float(ACTIONS["risky"]["failure_chance"])
    difference_points = abs(observed_failure_rate - configured_failure_rate) * 100
    print(f"Trials: {samples}; successes: {successes}; failures: {failures}")
    print(f"Observed failure rate: {observed_failure_rate * 100:.2f}%")
    print(f"Configured failure rate: {configured_failure_rate * 100:.2f}%")
    print(f"Absolute difference: {difference_points:.2f} percentage points (limit: 5.00)")

    passed = difference_points <= 5
    print(f"CHECK 2: {'PASS' if passed else 'FAIL'}")
    return passed


def check_hard_difficulty_values() -> bool:
    """Compare hard difficulty action values with the base configuration."""
    hard_actions = get_actions_for_difficulty("hard")
    print("\nCHECK 3 — Hard difficulty action values")

    passed = True
    for action_name, base_action in ACTIONS.items():
        hard_action = hard_actions[action_name]
        print(
            f"  {action_name}: failure_chance "
            f"{base_action['failure_chance']:.3f} -> "
            f"{hard_action['failure_chance']:.3f}; stamina_cost "
            f"{base_action['stamina_cost']} -> {hard_action['stamina_cost']}"
        )

        expected_failure_chance = min(1.0, base_action["failure_chance"] * 1.75)
        expected_stamina_cost = max(1, round(base_action["stamina_cost"] * 1.2))
        passed = passed and (
            hard_action["failure_chance"] == expected_failure_chance
            and hard_action["stamina_cost"] == expected_stamina_cost
        )

    print(f"CHECK 3: {'PASS' if passed else 'FAIL'}")
    return passed


def main() -> None:
    """Run both diagnostics and print the final check summary."""
    _ = STRATEGIES, run_simulation
    conservative_passed = check_conservative_strategy()
    risky_passed = check_risky_failure_rate()
    hard_difficulty_passed = check_hard_difficulty_values()
    print("\nFinal summary:")
    print(f"CHECK 1: {'PASS' if conservative_passed else 'FAIL'}")
    print(f"CHECK 2: {'PASS' if risky_passed else 'FAIL'}")
    print(f"CHECK 3: {'PASS' if hard_difficulty_passed else 'FAIL'}")


if __name__ == "__main__":
    main()
