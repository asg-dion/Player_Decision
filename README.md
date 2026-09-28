# Stamina Strategy Simulator

A Python and Flask web app that compares four decision-making strategies for spending a limited stamina resource. Every strategy faces the same actions and starting conditions across repeated runs, and the results are shown as a table and charts.

## What It Does

In many games, players must decide how to spend a limited resource. This project simulates that trade-off. Four rule-based strategies (conservative, aggressive, risk-taking, and balanced) are run through the same turn-based scenario, and their outcomes are compared using:

- Average score
- Success rate
- Stamina used
- Stamina remaining

There is no human player and no playable game. It is a controlled comparison of decision rules.

## The Four Strategies

| Strategy | Rule |
|---|---|
| Conservative | Acts only when stamina is above 40% of maximum stamina, and then picks the cheapest action (normal). Otherwise it saves stamina. |
| Aggressive | Picks the strong action whenever it can afford it, falling back to normal. |
| Risk-Taking | Picks the risky action whenever it can afford it, regardless of the odds, falling back to normal. |
| Balanced | Picks the affordable action with the best expected value per stamina cost: `reward * (1 - failure_chance) / stamina_cost`. |

## Simulation Settings

**Actions**

| Action | Stamina Cost | Reward | Failure Chance |
|---|---|---|---|
| Normal | 5 | 10 | 0% |
| Strong | 10 | 20 | 5% |
| Risky | 15 | 35 | 30% |

**Starting stamina levels:** low = 20, medium = 50, high = 100 (maximum stamina = 100).

All values are defined in `config.py`.

## Project Structure

```
stamina_sim/
├── app.py                # Flask app and API routes
├── config.py             # Actions, stamina levels, constants
├── strategies.py         # The four strategy functions
├── simulation.py         # Turn logic and simulation loop
├── run_experiment.py     # Batch experiment, saves CSV to results/
├── analyze_results.py    # Summary tables and charts from the CSV
├── tests.py              # Basic assert-based tests
├── diagnostics.py        # Checks strategy thresholds and failure-rate logic
├── templates/
│   └── index.html        # Dashboard page
├── static/
│   ├── style.css
│   ├── script.js
│   └── audio/            # Optional sound files
└── results/              # Generated CSVs and charts
```

## Requirements

- Python 3.10 or newer
- Flask
- pandas
- matplotlib (only needed for `analyze_results.py`)

Install with:

```bash
pip install flask pandas matplotlib
```

The dashboard loads Chart.js from a CDN, so an internet connection is needed the first time the page loads.

## Running the Dashboard

From the project folder:

```bash
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

In the dashboard you can:

1. Choose which strategies to include
2. Choose the starting stamina level (low, medium, or high)
3. Set the number of turns per run
4. Set the number of repetitions per strategy
5. Click **Run Simulation** to see the results table and charts
6. Download the raw results as a CSV

## Running the Batch Experiment

For reproducible data to use in a report, run the script version instead of the dashboard:

```bash
python tests.py
python diagnostics.py
python run_experiment.py
python analyze_results.py
```

This runs every strategy at every stamina level, saves the results to `results/experiment_results.csv`, and generates summary tables and charts.

## Testing

- `tests.py` checks that stamina never goes negative, that strategies never pick unaffordable actions, that failed actions award 0 points, and that every strategy runs at each stamina level.
- `diagnostics.py` prints the conservative strategy's threshold against each stamina level and checks that the observed failure rate of the risky action matches its configured value over 2,000 trials.

## Known Behavior

At the low stamina level (20), the conservative strategy never acts, because 20 never exceeds its threshold of 40. This produces a score of 0 and 0 stamina used for that strategy. This is a result of the rule as designed, and it shows how a fixed threshold can behave differently across starting conditions.

## Limitations

- No real human players are studied.
- The strategies are simplified rules, with no emotion, learning, or teamwork.
- Results apply only to the actions and values in `config.py`.
- Stamina is the only resource modeled.

## Possible Improvements

- Scale the conservative threshold to each run's starting stamina instead of a fixed maximum
- Add more actions, situations, or difficulty levels
- Add other resources such as health or money
- Add more strategies for comparison