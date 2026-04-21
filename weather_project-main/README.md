# Module 9: Phase 9 Submit - Flask Web Application

## Summary

- Added a 3-tier Flask web application in `src/app.py` that lets users interact with the weather data through a browser.
- Added `src/models.py` with a SQLAlchemy model to store query history in a SQLite database.
- Added HTML templates in `src/templates/` and basic CSS in `src/static/style.css`.
- Added `tests/test_app.py` with 7 tests covering the Flask routes.
- Updated `requirements.txt` with `flask`, `flask-sqlalchemy`, and `sqlalchemy`.

## What Was Added

**New Files:**
- `src/app.py` — Flask application with routes for stats, visualizations, and query history
- `src/models.py` — SQLAlchemy model (`QueryHistory`) storing column lookups in SQLite
- `src/templates/base.html` — Base Jinja template with nav bar
- `src/templates/index.html` — Home page with dataset and column selection form
- `src/templates/stats.html` — Displays descriptive statistics in a table
- `src/templates/viz.html` — Chart selection form and rendered plot
- `src/templates/history.html` — Lists past queries from the SQLite database
- `src/static/style.css` — Basic stylesheet
- `tests/test_app.py` — Flask route tests using the test client

**Modified:**
- `requirements.txt` — Added `flask>=2.3.0`, `flask-sqlalchemy>=3.0.0`, `sqlalchemy>=2.0.0`

## Application Structure

The app follows a 3-tier design:
- **Frontend (UI tier):** HTML/CSS templates rendered with Jinja2, served by Flask
- **Backend (logic tier):** Flask routes in `app.py` calling the existing `weatherstats` package for data processing and `matplotlib` for plots
- **Data tier:** SQLite database (via SQLAlchemy) storing query history; weather CSV files for the analysis data

## Pages

- **/** — Home page: pick a dataset (training or test) and a numeric column, submit to see stats
- **/stats** — Shows count, mean, median, mode, min, max, range, std dev, and variance for the selected column
- **/viz** — Pick a chart type and dataset, renders the chart as an embedded image. Chart options: Rainfall Histogram, Average Max Temp by Location, Humidity 9am vs 3pm
- **/history** — Shows the last 50 column lookups stored in the SQLite database

## SQLite / SQLAlchemy

The `QueryHistory` table stores each time a user requests statistics for a column. Fields: `id`, `column`, `dataset`, and `queried_at` (timestamp). This lets you see what the app has been used to look at over time. The database file is created automatically at `src/weather_app.db` on first run.

## Run Instructions

1. Navigate to the project folder:
```bash
cd "Weather project"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Flask app:
```bash
python3 src/app.py
```

4. Open a browser and go to:
```
http://127.0.0.1:5000
```

5. Run all tests (including the new Flask tests):
```bash
pytest -v tests/
```

6. Run just the Flask tests:
```bash
pytest -v tests/test_app.py
```

## Test Coverage

### Flask Tests (`test_app.py`)

| Test | What It Covers |
|---|---|
| `test_home_page_loads` | GET / returns 200 |
| `test_history_page_loads` | GET /history returns 200 |
| `test_viz_page_loads` | GET /viz returns 200 |
| `test_stats_invalid_column` | Invalid column shows error message |
| `test_stats_valid_column` | Valid column returns stats table |
| `test_history_records_query` | Query is saved to DB and shows in history |
| `test_home_page_has_column_options` | Column dropdowns are present |

### Previous Phase Tests (still passing)

| Test File | Tests | Coverage |
|---|---|---|
| `test_weatherstats.py` | 38 | CSV loading, generators, store, analyzer, integration |
| `test_io_async.py` | 10 | Async I/O parity |
| `test_stats_parallel.py` | 10 | Parallel stats accuracy |
| `test_viz_parallel.py` | 13 | Parallel plotting parity |
| `test_viz.py` | 1 | Basic plot generation |
| `test_pyspark.py` | 31 | PySpark implementation |
| **Total** | **79** | |
