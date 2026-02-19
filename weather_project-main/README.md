# Module 6: Phase 6 Submit - Data Patterns, Trends, Visualize

Summary
- Added visualization helpers: `src/weatherstats/viz.py` — plotting functions using `seaborn` and `matplotlib`. These include simple functional examples using `map`, `filter`, `reduce`, and `lambda` to demonstrate required concepts.
- Added a CLI to generate static visuals: `scripts/visualize.py`. Running this creates PNGs in `Weather project/visualizations/`.
- Added a lightweight plot smoke test: `tests/test_viz.py` that runs the plotting pipeline on the test CSV and checks that `total_rainfall` is computed and at least one image is produced.
- Updated `requirements.txt` to include plotting libraries (`matplotlib`, `seaborn`).

Files of interest (changed or new)
- `src/weatherstats/viz.py` — new: plotting helpers and small functional examples.
- `scripts/visualize.py` — new: CLI that saves PNG charts.
- `tests/test_viz.py` — new: lightweight smoke test for plots.
- `requirements.txt` — updated to include plotting libraries.

What I produced
- Static visualizations saved to `Weather project/visualizations/` (examples included):
  - `max_temp_histogram.png`
  - `rainfall_histogram.png`
  - `temp_vs_rain_scatter.png`
  - `box_temps_by_location.png`
  - `top_locations_by_rain.png`
  - `run_success.png` (summary image showing the run completed)

Why these were chosen
- The charts demonstrate distributional properties (histograms), relationships (scatter), and group comparisons (boxplots and bar charts) so trends and patterns are easy to inspect visually.

Minimal run instructions
1) From the repository root, go to the project folder:
```bash
cd "Weather project"
```
2) Install dependencies (recommended virtual environment):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
3) Generate visualizations:
```bash
python3 scripts/visualize.py
```

Automated checks included
- Existing tests for data loading, generator, `WeatherDataStore`, and `WeatherAnalyzer` (unchanged).
- New `tests/test_viz.py` smoke test for the plotting pipeline.

Notes and assumptions
- Some CSV fields include `NA` or missing values; numeric conversions use `errors='coerce'` and NaNs are ignored for plotting.
- The supplied CSVs do not contain a usable `Date` column; the code attempts a date-based time series if present, otherwise it produces the fallback static charts listed above.
