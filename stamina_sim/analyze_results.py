"""Summarize experiment results and generate comparison charts."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    project_directory = Path(__file__).resolve().parent
    results_directory = project_directory / "results"
    csv_path = results_directory / "experiment_results.csv"
    results = pd.read_csv(csv_path)
    summary = (
        results.groupby(["difficulty", "strategy", "stamina_level"])[
            ["final_score", "success_rate", "stamina_used", "stamina_remaining"]
        ]
        .mean()
        .sort_index()
    )
    print("Average results by difficulty, strategy, and stamina level:")
    print(summary.to_string(float_format=lambda value: f"{value:.3f}"))

    difficulty_order = ["easy", "medium", "hard"]
    stamina_order = ["low", "medium", "high"]
    chart_index = pd.MultiIndex.from_product(
        [difficulty_order, stamina_order],
        names=["difficulty", "stamina_level"],
    )
    for metric, title, ylabel, filename in (
        (
            "final_score",
            "Average Score by Difficulty and Stamina Level",
            "Average score",
            "score_comparison.png",
        ),
        (
            "success_rate",
            "Average Success Rate by Difficulty and Stamina Level",
            "Average success rate",
            "success_rate_comparison.png",
        ),
    ):
        chart_data = (
            summary[metric]
            .unstack("strategy")
            .reindex(chart_index)
        )
        chart_data.index = [
            f"{difficulty.title()} / {stamina.title()}"
            for difficulty, stamina in chart_data.index
        ]
        axis = chart_data.plot(kind="bar", figsize=(9, 5), width=0.8)
        axis.set_title(title)
        axis.set_xlabel("Difficulty / stamina level")
        axis.set_ylabel(ylabel)
        axis.legend(title="Strategy")
        axis.grid(axis="y", alpha=0.25)
        axis.figure.tight_layout()
        chart_path = results_directory / filename
        axis.figure.savefig(chart_path, dpi=150)
        plt.close(axis.figure)
        print(f"Saved chart to {chart_path}")


if __name__ == "__main__":
    main()
