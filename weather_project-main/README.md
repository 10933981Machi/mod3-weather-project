# Module 7: Phase 7 Submit - Multithreading Concurrency

## Summary

- Added async I/O wrappers: `async_load_weather_csv()` and `weather_records_generator_async()` in `src/weatherstats/io.py` using `asyncio.to_thread()` to prevent blocking the event loop.
- Added parallel statistics: `descriptive_stats_parallel()` in `src/weatherstats/stats.py` using `ProcessPoolExecutor` to distribute per-column stats computation across multiple CPU cores.
- Added parallel plotting: `create_all_plots_parallel()` in `src/weatherstats/viz.py` to generate independent plots concurrently via `ProcessPoolExecutor`.
- Added CLI flags `--parallel` and `--workers N` to `scripts/visualize.py` for easy parallel execution testing.
- Updated `requirements.txt` with `aiofiles>=23.0.0` for async file operations.
- Added comprehensive parity tests: `tests/test_io_async.py`, `tests/test_stats_parallel.py`, `tests/test_viz_parallel.py` verifying async/parallel versions match synchronous versions within numeric tolerance.

## Files Changed or Added

**Modified:**
- `src/weatherstats/io.py` — async CSV loading and record generator
- `src/weatherstats/stats.py` — parallel descriptive statistics
- `src/weatherstats/viz.py` — parallel plot generation
- `scripts/visualize.py` — argparse options for `--parallel` and `--workers`
- `requirements.txt` — added `aiofiles>=23.0.0`

**New Test Files:**
- `tests/test_io_async.py` — async I/O parity tests
- `tests/test_stats_parallel.py` — parallel stats parity tests
- `tests/test_viz_parallel.py` — parallel plotting parity tests

## Async Features

- **`async_load_weather_csv()`**: Non-blocking CSV load via `asyncio.to_thread()`. Prevents event loop blocking during I/O.
- **`weather_records_generator_async()`**: Async generator yielding records without blocking. Enables concurrent record streaming.

## Parallelism Features

- **`descriptive_stats_parallel(columns, workers=None)`**: Distributes per-column stats computation to multiple processes. Default workers = `os.cpu_count()`.
- **`create_all_plots_parallel(csv_path, output_dir, workers=None)`**: Renders independent plots concurrently. Each worker loads CSV fresh and generates one plot safely.

## Run Instructions

1) From repository root:
```bash
cd "Weather project"
```

2) Install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3) Run tests:
```bash
pytest -v tests/
```

4) Generate visualizations:
```bash
# Serial mode
python3 scripts/visualize.py

# Parallel mode (auto-detect workers)
python3 scripts/visualize.py --parallel

## Test Coverage

- **`test_io_async.py`**: Verifies async loads and generators produce identical results to sync versions; tests concurrent operations.
- **`test_stats_parallel.py`**: Verifies parallel stats match serial stats within tolerance (1e-6); tests variable worker counts.
- **`test_viz_parallel.py`**: Verifies parallel plots match serial plots; checks file creation and total_rainfall computation.