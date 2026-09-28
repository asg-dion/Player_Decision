"""Run each strategy at every configured stamina level and save run results."""

import os

import pandas as pd

from config import STAMINA_LEVELS
from simulation import run_simulation
from strategies import STRATEGIES


def main() -> None:
    rows = []

    for stamina_level, starting_stamina in STAMINA_LEVELS.items():
        for strategy_name, strategy_function in STRATEGIES.items():
            for _ in range(100):
                result = run_simulation(
                    strategy_function,
                    starting_stamina,
                    num_turns=20,
                )
                turns_completed = result["turns_completed"]
                success_rate = (
                    result["successes"] / turns_completed if turns_completed else 0
                )
                rows.append(
                    {
                        "strategy": strategy_name,
                        "stamina_level": stamina_level,
                        "starting_stamina": starting_stamina,
                        "final_score": result["total_score"],
                        "success_rate": success_rate,
                        "stamina_used": starting_stamina - result["final_stamina"],
                        "stamina_remaining": result["final_stamina"],
                    }
                )

    results = pd.DataFrame(rows)
    results_directory = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_directory, exist_ok=True)
    output_path = os.path.join(results_directory, "experiment_results.csv")
    results.to_csv(output_path, index=False)
    print(f"Saved {len(results)} rows to {output_path}")


if __name__ == "__main__":
    main()