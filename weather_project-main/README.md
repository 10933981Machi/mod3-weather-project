# Module 8: Phase 8 Submit - PySpark

## Summary

- Added `src/weatherstats/spark_weather.py` with a full PySpark implementation of the weather analysis pipeline using SparkSession, Spark DataFrames, and Spark SQL.
- Added `scripts/run_spark_demo.py` to demonstrate all PySpark features end-to-end including data loading, descriptive stats, filtering, aggregations, and SQL queries.
- Added `tests/test_pyspark.py` with 31 tests covering session creation, CSV loading, stats accuracy, filtering, aggregations, Spark SQL, and parity checks against the pandas implementation.
- Updated `requirements.txt` with `pyspark>=3.4.0`.
- See `CONSIDERATIONS.md` for a full description of what had to change to run on a PySpark cluster.

## Files Changed or Added

**New Files:**
- `src/weatherstats/spark_weather.py` — PySpark module: SparkSession creation, CSV loading, descriptive stats, filtering, groupBy aggregations, Spark SQL analysis
- `scripts/run_spark_demo.py` — Demo script running all PySpark features against the training dataset
- `tests/test_pyspark.py` — 31 PySpark tests compared against the existing pandas implementation
- `CONSIDERATIONS.md` — Describes what was considered and changed to migrate to PySpark

**Modified:**
- `requirements.txt` — Added `pyspark>=3.4.0`

## PySpark Features

- **`create_spark_session()`** — Builds a local SparkSession using `local[*]` to use all CPU cores
- **`load_weather_csv_spark()`** — Loads the weather CSV into a distributed Spark DataFrame
- **`descriptive_stats_spark(column)`** — Computes count, mean, median, mode, min, max, range, std, variance via Spark aggregation functions
- **`descriptive_stats_all_spark(columns)`** — Runs stats across multiple columns
- **`filter_rainy_days_spark()`** — Filters rows where Rainfall > 0 using Spark
- **`high_temperature_days_spark(threshold)`** — Filters rows where MaxTemp >= threshold
- **`total_rainfall_spark()`** — Sums total rainfall using `F.sum()` across all partitions
- **`avg_temp_by_location_spark()`** — GroupBy Location, average MinTemp and MaxTemp
- **`avg_rainfall_by_location_spark()`** — GroupBy Location, average Rainfall
- **`rain_today_counts_spark()`** — Counts RainToday category distribution
- **`spark_sql_analysis()`** — Registers a SQL temp view and queries top hottest/wettest locations, overall summary, and rain distribution

## Run Instructions

1. Navigate to the project folder:
```bash
cd "Weather project"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the PySpark demo:
```bash
python3 scripts/run_spark_demo.py
```

4. Run PySpark tests:
```bash
pytest -v tests/test_pyspark.py
```

5. Run all tests:
```bash
pytest -v tests/
```

## Test Coverage

### PySpark Tests (`test_pyspark.py`)

| Test Class | Tests | What It Covers |
|---|---|---|
| `TestSparkSession` | 3 | Session creation, app name, local master |
| `TestLoadCSV` | 5 | DataFrame loading, row/column count parity, error handling |
| `TestDescriptiveStats` | 7 | Stats keys, count/mean/min/max accuracy, multi-column |
| `TestFiltering` | 4 | Rainy days filter, high temp filter, custom thresholds |
| `TestAggregations` | 5 | Total rainfall, averages by location, rain counts |
| `TestSparkSQL` | 4 | SQL query results, hottest locations, summary values |
| `TestPandasParity` | 3 | Spark vs pandas stats comparison within tolerance |
| **Total** | **31** | |

### Previous Phase Tests (still passing)

| Test File | Tests | Coverage |
|---|---|---|
| `test_weatherstats.py` | 38 | CSV loading, generators, store, analyzer, integration |
| `test_io_async.py` | 10 | Async I/O parity |
| `test_stats_parallel.py` | 10 | Parallel stats accuracy |
| `test_viz_parallel.py` | 13 | Parallel plotting parity |
| `test_viz.py` | 1 | Basic plot generation |
| **Total** | **72** | |