# Module 11: Final Project - Australian Weather Analytics Dashboard

## Summary

Built out the full final project as a secure, interactive 3-tier web application. Added user authentication (login/logout), a CSV upload screen, and a single-page interactive analytics dashboard with three category buttons, a dynamic city dropdown, and charts that load without page reloads.

## What Was Added

**New Files:**
- `src/templates/login.html` — Login page with username/password form
- `src/templates/upload.html` — CSV upload screen shown after login
- `src/templates/dashboard.html` — Single-page dashboard with 3 category buttons, city dropdown, and AJAX chart updates
- `tests/test_dashboard.py` — 18 tests covering auth, upload, dashboard, and API routes

**Modified:**
- `src/app.py` — Added login/logout/upload/dashboard routes, `/api/cities` and `/api/chart` JSON endpoints, `login_required` decorator protecting all routes, context processor for username injection
- `src/models.py` — Added `User` model with hashed password storage
- `src/templates/base.html` — Updated nav with Dashboard link, Stats link, and logged-in username/logout on the right
- `tests/test_app.py` — Rewritten with login fixtures for auth-protected routes

## Application Architecture

The app follows a three-tier structure:

**Presentation layer** — Jinja2 HTML templates handle all rendering. The dashboard page uses vanilla JavaScript `fetch()` calls to update charts and the city dropdown without reloading the page.

**Application layer** — All logic lives in `app.py`. Flask routes handle login sessions, validate uploaded files, run pandas analysis on the CSV data, and generate matplotlib charts encoded as base64 strings.

**Data layer** — SQLite (accessed through SQLAlchemy) stores user accounts, query history, and prediction logs. Uploaded CSV files are written to `src/uploads/`.

## Authentication

- Users stored in the `users` table with `werkzeug` password hashing (`generate_password_hash` / `check_password_hash`)
- A default user is seeded on startup: **username: `admin`, password: `password`**
- Login state is tracked via Flask's signed session cookie
- A `login_required` decorator wraps every protected route and redirects unauthenticated requests to `/login`
- The CSV path stored in session is validated against the upload directory to prevent path traversal

## Dashboard Flow

1. User logs in → redirected to the CSV upload page
2. User uploads a CSV file → redirected to the interactive dashboard
3. On the dashboard, user clicks one of three category buttons:
   - **Temperature Trends** — line chart of MinTemp / MaxTemp over records
   - **Rainfall Patterns** — histogram of rainfall on rainy days
   - **Extreme Weather** — bar chart of hot days and humid afternoons
4. Clicking a button triggers a `fetch('/api/cities')` call that populates the city dropdown
5. Selecting a city triggers `fetch('/api/chart?category=...&city=...')` which returns a base64 chart image and text summary
6. The chart and summary update in-place — no page load

## Pages

- **/login** — Login screen
- **/upload** — CSV upload (login required)
- **/dashboard** — Interactive dashboard (login required, CSV required)
- **/stats** — Descriptive statistics lookup from Phase 9 (login required)
- **/viz** — Static chart visualizations from Phase 9 (login required)
- **/predict** — Rain tomorrow prediction from Phase 10 (login required)
- **/history** — Query history stored in SQLite (login required)

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

5. Login with: **username: `admin`**, **password: `password`**

6. Upload one of the CSV files from the `Data/` folder

7. Use the dashboard buttons and city dropdown to explore the data

8. Run all tests:
```bash
pytest -v tests/
```

9. Run just the dashboard/auth tests:
```bash
pytest -v tests/test_dashboard.py tests/test_app.py
```

## Test Coverage

### Dashboard / Auth Tests (`test_dashboard.py`)

| Test Class | Tests | What It Covers |
|---|---|---|
| `TestLoginUploadRoutes` | 6 | Login page, valid/invalid credentials, upload protection, non-CSV rejection |
| `TestDashboardRoutes` | 4 | Login required, CSV required redirect, dashboard loads, buttons present |
| `TestAPIRoutes` | 8 | Cities list, sorted order, chart endpoints for all 3 categories, error cases |
| **Total** | **18** | |

### App Tests (`test_app.py`)

| Test Class | Tests | What It Covers |
|---|---|---|
| `TestAuth` | 7 | Login, logout, route protection for unauthenticated users |
| `TestRoutes` | 7 | Stats lookup, viz, history, column options |
| **Total** | **14** | |

### All Phase Tests

| Test File | Tests | Coverage |
|---|---|---|
| `test_dashboard.py` | 18 | Auth, upload, dashboard, API routes |
| `test_app.py` | 14 | Flask routes, DB logging |
| `test_predictor.py` | 15 | ML model training and prediction |
| `test_weatherstats.py` | 38 | CSV loading, generators, store, analyzer |
| `test_io_async.py` | 10 | Async I/O parity |
| `test_stats_parallel.py` | 10 | Parallel stats accuracy |
| `test_viz_parallel.py` | 13 | Parallel plotting parity |
| `test_viz.py` | 1 | Basic plot generation |
| `test_pyspark.py` | 31 | PySpark implementation (requires Java 17) |
| **Total** | **150** | |

## Development Phase Summary

| Phase | What Was Built |
|---|---|
| Phase 4 | `weatherstats` package: CSV loading, OOP stats, generators |
| Phase 5 | Async I/O, parallel processing with `ProcessPoolExecutor` |
| Phase 6 | `viz.py`: matplotlib/seaborn plotting with functional programming |
| Phase 7 | Parallel plot rendering, parity tests |
| Phase 8 | PySpark migration: SparkSession, distributed stats, Spark SQL |
| Phase 9 | Flask 3-tier web app, SQLAlchemy query history, Jinja2 templates |
| Phase 10 | scikit-learn `RandomForestClassifier` for rain tomorrow prediction |
| Phase 11 | Login/auth, CSV upload flow, single-page interactive dashboard |
