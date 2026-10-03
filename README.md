# Stamina Strategy Simulator

A Python and Flask web app with a teal, sage, and cream color theme that compares four decision-making strategies for spending a limited stamina resource. Each run varies the selected strategy, starting stamina level, and situation difficulty. Results are shown as a summary table and charts.

## What It Does

In many games, players must decide how to spend a limited resource. This project simulates that trade-off. Four rule-based strategies (conservative, aggressive, risk-taking, and balanced) are run through the same turn-based scenario, and their outcomes are compared using:

- Average score
- Success rate
- Stamina used
- Stamina remaining

The Flask dashboard lets users choose strategies, stamina, turns, repetitions, and difficulty. Difficulty scales each action's failure chance and stamina cost for that run. There is no human player and no playable game; it is a controlled comparison of decision rules.

## The Four Strategies

| Strategy | Rule |
|---|---|
| Conservative | Acts only when stamina is above 40% of maximum stamina, and then picks the cheapest action (normal). Otherwise it saves stamina. |
| Aggressive | Picks the strong action whenever it can afford it, falling back to normal. |
| Risk-Taking | Picks the risky action whenever it can afford it, regardless of the odds, falling back to normal. |
| Balanced | Picks the affordable action with the best expected value per stamina cost: `reward * (1 - failure_chance) / stamina_cost`. |

Each strategy receives the difficulty-adjusted action values for the run. Therefore, its behavior and outcomes can change with the selected situation difficulty, which scales failure chance and stamina cost.

## Simulation Settings

**Actions**

| Action | Stamina Cost | Reward | Failure Chance |
|---|---:|---:|---:|
| Normal | 5 | 10 | 0% |
| Strong | 10 | 20 | 5% |
| Risky | 15 | 35 | 30% |

**Starting stamina levels:** low = 20, medium = 50, high = 100 (maximum stamina = 100).

**Difficulty Levels**

| Difficulty | Failure Chance Multiplier | Stamina Cost Multiplier |
|---|---:|---:|
| Easy | x0.5 | x1.0 |
| Medium | x1.0 | x1.0 |
| Hard | x1.75 | x1.2 |

Difficulty values match `DIFFICULTY_LEVELS` in `config.py`. Adjusted failure chances are capped at 1.0, and adjusted stamina costs are rounded to the nearest integer with a minimum of 1.

All simulation values are defined in `config.py`.

## Project Structure

```
stamina_sim/
|-- app.py                # Flask dashboard and API routes
|-- config.py             # Actions, difficulty levels, stamina levels, constants
|-- strategies.py         # The four strategy functions
|-- simulation.py         # Turn logic and simulation loop
|-- run_experiment.py     # Batch experiment, saves CSV to results/
|-- analyze_results.py    # Summary tables and charts from the CSV
|-- tests.py              # Basic assert-based tests
|-- diagnostics.py        # Strategy, failure-rate, and difficulty checks
|-- requirements.txt      # Python dependencies
|-- templates/
|   `-- index.html        # Dashboard page
|-- static/
|   |-- style.css         # Dashboard styling
|   |-- script.js         # Dashboard behavior and API requests
|   `-- audio/
|       |-- background.mp3
|       `-- bling.mp3
`-- results/              # Generated CSV and chart files
```

## Requirements

- Python 3.10 or newer
- Flask
- pandas
- matplotlib (needed for `analyze_results.py`)

Install with:

```bash
pip install -r stamina_sim/requirements.txt
```

The dashboard loads Chart.js from a CDN, so an internet connection is needed the first time the page loads.

## Running the Dashboard

From the project folder:

```bash
cd stamina_sim
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

In the dashboard you can:

1. Choose which strategies to include
2. Choose the starting stamina level (low, medium, or high)
3. Choose the situation difficulty (easy, medium, or hard)
4. Set the number of turns per run
5. Set the number of repetitions per strategy
6. Click **Run Simulation** to see the results table and charts
7. Download the completed run's raw results as a CSV

The speaker button controls the background music, and action feedback uses the included sound effect.

## Running the Batch Experiment

For data to use in a report, run the script version instead of the dashboard:

```bash
cd stamina_sim
python tests.py
python diagnostics.py
python run_experiment.py
python analyze_results.py
```

The batch experiment runs every strategy at every stamina level and difficulty level, with 100 repetitions per combination: 4 strategies x 3 stamina levels x 3 difficulties x 100 repetitions = 3,600 rows. It saves the results to `results/experiment_results.csv` and generates summary tables and charts grouped by difficulty, strategy, and stamina level.

## Testing

- `tests.py` checks that stamina never goes negative, strategies never pick unaffordable actions, failed actions award 0 points, and every strategy runs at each stamina level.
- `diagnostics.py` checks conservative threshold behavior, measures the risky action's failure rate over 2,000 trials, and verifies the hard-difficulty failure and cost multipliers against the base `ACTIONS` values.

## Known Behavior

At the low stamina level (20), the conservative strategy never acts, because 20 never exceeds its threshold of 40. This produces a score of 0 and 0 stamina used for that strategy. This is a result of the rule as designed, and it shows how a fixed threshold can behave differently across starting conditions.

At hard difficulty, every action's failure chance is scaled up by 1.75 and capped at 100%, while stamina costs are increased by 1.2. This can make risk-taking and aggressive strategies perform noticeably worse than at easy or medium difficulty.

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
