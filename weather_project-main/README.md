# Module 10: Phase 10 Submit - Predictive Modeling Scikit-Learn

## Summary

- Added `src/weatherstats/predictor.py` with a RandomForestClassifier that predicts whether it will rain tomorrow based on today's weather conditions.
- Added a `/predict` route and `src/templates/predict.html` to the Flask app so users can enter weather values and get a prediction in the browser.
- Added `src/models.py` `PredictionLog` table to store each prediction in the SQLite database.
- Added `tests/test_predictor.py` with 15 tests covering model training, accuracy, and prediction output.
- Updated `requirements.txt` with `scikit-learn>=1.3.0`.

## What Was Added

**New Files:**
- `src/weatherstats/predictor.py` — builds and trains a RandomForestClassifier, exposes `build_model()` and `predict_rain()`
- `src/templates/predict.html` — form for entering today's conditions and displaying the rain prediction
- `tests/test_predictor.py` — 15 tests for the ML model

**Modified:**
- `src/app.py` — added `/predict` GET/POST route
- `src/models.py` — added `PredictionLog` SQLAlchemy model
- `src/templates/base.html` — added Rain Prediction link to nav
- `src/static/style.css` — added styles for prediction result box and number inputs
- `requirements.txt` — added `scikit-learn>=1.3.0`

## Machine Learning Details

**Model:** RandomForestClassifier (100 trees, `random_state=42`)

**Target:** `RainTomorrow` (Yes / No)

**Features used:**
- MinTemp, MaxTemp, Rainfall
- Humidity9am, Humidity3pm
- Pressure9am, Pressure3pm
- WindGustSpeed

**Process:**
1. Load the training CSV
2. Drop rows with missing target or feature values
3. Encode target with `LabelEncoder` (No=0, Yes=1)
4. Split 80/20 train/test with `train_test_split`
5. Train `RandomForestClassifier`
6. Evaluate with `accuracy_score` and `classification_report`
7. On form submit, run `model.predict()` and `model.predict_proba()` to show the prediction and probability

Test set accuracy on the training dataset is consistently above 85%.

## Application Pages (updated)

- **/** — Stats lookup
- **/viz** — Charts
- **/predict** — Enter today's weather values and get a rain forecast with probability
- **/history** — Query history from SQLite

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

5. To run just the ML tests:
```bash
pytest -v tests/test_predictor.py
```

6. Run all tests:
```bash
pytest -v tests/
```

## Test Coverage

### ML Tests (`test_predictor.py`)

| Test Class | Tests | What It Covers |
|---|---|---|
| `TestBuildModel` | 8 | model keys, accuracy > 80%, report format, feature/target constants |
| `TestPredictRain` | 7 | return type, keys, Yes/No label, probability range, high/low humidity cases |
| **Total** | **15** | |

### Previous Phase Tests (still passing)

| Test File | Tests | Coverage |
|---|---|---|
| `test_app.py` | 7 | Flask routes, DB logging |
| `test_weatherstats.py` | 38 | CSV loading, generators, store, analyzer |
| `test_io_async.py` | 10 | Async I/O parity |
| `test_stats_parallel.py` | 10 | Parallel stats accuracy |
| `test_viz_parallel.py` | 13 | Parallel plotting parity |
| `test_viz.py` | 1 | Basic plot generation |
| `test_pyspark.py` | 31 | PySpark implementation (requires Java 17) |
| **Total** | **110** | |
