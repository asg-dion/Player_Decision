"""Flask endpoints for the stamina strategy simulator."""

import json

import pandas as pd
from flask import Flask, Response, jsonify, render_template, request

from config import DIFFICULTY_LEVELS, STAMINA_LEVELS, get_actions_for_difficulty
from simulation import run_simulation
from strategies import STRATEGIES

app = Flask(__name__)


def _get_run_parameters() -> tuple[list[str], str, int, str, int, int]:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")

    selected_strategies = payload.get("strategies")
    stamina_level = payload.get("stamina_level")
    difficulty = payload.get("difficulty", "medium")
    turns = payload.get("turns")
    repetitions = payload.get("repetitions")

    if (
        not isinstance(selected_strategies, list)
        or not selected_strategies
        or any(not isinstance(name, str) or name not in STRATEGIES for name in selected_strategies)
    ):
        raise ValueError("strategies must be a non-empty list of known strategy names.")
    if not isinstance(stamina_level, str) or stamina_level not in STAMINA_LEVELS:
        raise ValueError("stamina_level must be low, medium, or high.")
    if not isinstance(difficulty, str) or difficulty not in DIFFICULTY_LEVELS:
        raise ValueError("difficulty must be easy, medium, or hard.")
    if type(turns) is not int or turns <= 0:
        raise ValueError("turns must be a positive integer.")
    if type(repetitions) is not int or repetitions <= 0:
        raise ValueError("repetitions must be a positive integer.")

    return (
        selected_strategies,
        stamina_level,
        STAMINA_LEVELS[stamina_level],
        difficulty,
        turns,
        repetitions,
    )


def _generate_raw_results(
    selected_strategies: list[str],
    starting_stamina: int,
    actions_dict: dict[str, dict[str, int | float]],
    turns: int,
    repetitions: int,
) -> list[dict[str, str | int | float]]:
    rows = []
    for strategy_name in selected_strategies:
        strategy_function = STRATEGIES[strategy_name]
        for _ in range(repetitions):
            result = run_simulation(
                strategy_function, starting_stamina, turns, actions_dict
            )
            turns_completed = result["turns_completed"]
            rows.append(
                {
                    "strategy": strategy_name,
                    "final_score": result["total_score"],
                    "success_rate": (
                        result["successes"] / turns_completed if turns_completed else 0
                    ),
                    "stamina_used": starting_stamina - result["final_stamina"],
                    "stamina_remaining": result["final_stamina"],
                }
            )
    return rows


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/api/strategies")
def get_strategies() -> Response:
    return Response(
        json.dumps(list(STRATEGIES.keys())),
        mimetype="application/json",
    )


@app.get("/api/stamina-levels")
def get_stamina_levels() -> Response:
    return Response(
        json.dumps(STAMINA_LEVELS),
        mimetype="application/json",
    )


@app.get("/api/difficulty-levels")
def get_difficulty_levels() -> Response:
    return Response(
        json.dumps(list(DIFFICULTY_LEVELS.keys())),
        mimetype="application/json",
    )


@app.post("/api/run")
# Example: curl -X POST http://127.0.0.1:5000/api/run -H "Content-Type: application/json" -d '{"strategies":["balanced","risk_taking"],"stamina_level":"medium","turns":20,"repetitions":3}'
def run_experiment_api():
    try:
        (
            selected_strategies,
            _,
            starting_stamina,
            difficulty,
            turns,
            repetitions,
        ) = _get_run_parameters()
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    actions_dict = get_actions_for_difficulty(difficulty)
    rows = _generate_raw_results(
        selected_strategies, starting_stamina, actions_dict, turns, repetitions
    )

    result_columns = [
        "strategy",
        "final_score",
        "success_rate",
        "stamina_used",
        "stamina_remaining",
    ]
    results_frame = pd.DataFrame(rows, columns=result_columns)
    summary_frame = (
        results_frame.groupby("strategy", as_index=False)[
            ["final_score", "success_rate", "stamina_used", "stamina_remaining"]
        ]
        .mean()
    )
    return jsonify(
        {
            "raw_results": rows,
            "summary": summary_frame.to_dict(orient="records"),
        }
    )


@app.post("/api/download")
def download_results_api():
    try:
        (
            selected_strategies,
            stamina_level,
            starting_stamina,
            difficulty,
            turns,
            repetitions,
        ) = _get_run_parameters()
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    actions_dict = get_actions_for_difficulty(difficulty)
    rows = _generate_raw_results(
        selected_strategies, starting_stamina, actions_dict, turns, repetitions
    )
    csv_data = pd.DataFrame(
        rows,
        columns=[
            "strategy",
            "final_score",
            "success_rate",
            "stamina_used",
            "stamina_remaining",
        ],
    ).to_csv(index=False)
    response = Response(csv_data, mimetype="text/csv")
    response.headers["Content-Disposition"] = (
        f'attachment; filename="stamina_sim_{stamina_level}_{turns}turns_{repetitions}reps.csv"'
    )
    return response


if __name__ == "__main__":
    app.run(debug=True)
