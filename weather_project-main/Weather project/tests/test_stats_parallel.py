"""
test_stats_parallel.py

Tests for parallel statistics computation in weatherstats.stats module.
Verifies that parallel functions produce identical results to their synchronous counterparts.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from weatherstats.io import load_weather_csv
from weatherstats.stats import WeatherDataStore, WeatherAnalyzer


@pytest.fixture
def data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent.parent / "Data"


@pytest.fixture
def csv_file(data_dir):
    """Return path to training CSV."""
    return data_dir / "Weather Training Data.csv"


@pytest.fixture
def weather_analyzer(csv_file):
    """Create a WeatherAnalyzer with loaded data."""
    df = load_weather_csv(csv_file)
    store = WeatherDataStore(df)
    return WeatherAnalyzer(store)


@pytest.fixture
def numeric_columns(csv_file):
    """Get numeric columns from the CSV."""
    df = load_weather_csv(csv_file)
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    return numeric_cols[:5]  # Use first 5 numeric columns for faster tests


class TestParallelStats:
    """Test parallel statistics computation."""
    
    def test_parallel_stats_returns_list(self, weather_analyzer):
        """Parallel stats should return a list of dicts."""
        results = weather_analyzer.descriptive_stats_parallel(["Rainfall"])
        assert isinstance(results, list), "Should return a list"
        assert len(results) > 0, "Should have at least one result"
    
    def test_parallel_stats_single_column(self, weather_analyzer):
        """Parallel and serial stats should match for single column."""
        column = "Rainfall"
        
        serial_stats = weather_analyzer.descriptive_stats(column)
        parallel_stats = weather_analyzer.descriptive_stats_parallel([column])[0]
        
        # Compare keys
        assert set(serial_stats.keys()) == set(parallel_stats.keys()), \
            "Result dictionaries should have same keys"
        
        # Compare numeric values with tolerance
        tolerance = 1e-6
        for key in ["count", "mean", "median", "min", "max", "range", "std", "var"]:
            if key in serial_stats and key in parallel_stats:
                if serial_stats[key] is not None and parallel_stats[key] is not None:
                    assert abs(serial_stats[key] - parallel_stats[key]) < tolerance, \
                        f"Value for {key} should match: serial={serial_stats[key]}, parallel={parallel_stats[key]}"
    
    def test_parallel_stats_multiple_columns(self, weather_analyzer, numeric_columns):
        """Parallel stats should handle multiple columns."""
        results = weather_analyzer.descriptive_stats_parallel(numeric_columns, workers=2)
        
        assert len(results) == len(numeric_columns), \
            f"Should have {len(numeric_columns)} results, got {len(results)}"
        
        # Verify each result has the column name
        for i, col in enumerate(numeric_columns):
            assert results[i]["column"] == col, \
                f"Result {i} should be for column {col}"
    
    def test_parallel_vs_serial_match(self, weather_analyzer, numeric_columns):
        """Serial and parallel results should match (with numeric tolerance)."""
        tolerance = 1e-6
        
        serial_results = {col: weather_analyzer.descriptive_stats(col) for col in numeric_columns}
        parallel_results = {r["column"]: r for r in weather_analyzer.descriptive_stats_parallel(numeric_columns)}
        
        for col in numeric_columns:
            serial = serial_results[col]
            parallel = parallel_results.get(col, {})
            
            # Skip if there's an error
            if "error" in serial or "error" in parallel:
                continue
            
            # Compare numeric fields
            for key in ["count", "mean", "median", "min", "max", "range", "std", "var"]:
                if key in serial and key in parallel:
                    s_val = serial[key]
                    p_val = parallel[key]
                    if s_val is not None and p_val is not None:
                        assert abs(s_val - p_val) < tolerance, \
                            f"Column {col}: {key} mismatch: serial={s_val}, parallel={p_val}"
    
    def test_parallel_stats_with_workers(self, weather_analyzer, numeric_columns):
        """Parallel stats should accept custom worker count."""
        results_1 = weather_analyzer.descriptive_stats_parallel(numeric_columns, workers=1)
        results_2 = weather_analyzer.descriptive_stats_parallel(numeric_columns, workers=2)
        
        assert len(results_1) == len(results_2), "Should handle different worker counts"
    
    def test_parallel_stats_invalid_column(self, weather_analyzer):
        """Parallel stats should handle invalid columns gracefully."""
        results = weather_analyzer.descriptive_stats_parallel(["NonExistentColumn"])
        assert len(results) > 0, "Should return result even for invalid column"
        assert "error" in results[0], "Should indicate error for invalid column"
    
    def test_parallel_stats_default_workers(self, weather_analyzer, numeric_columns):
        """Parallel stats should use default worker count when not specified."""
        results = weather_analyzer.descriptive_stats_parallel(numeric_columns)
        assert len(results) == len(numeric_columns), "Should work with default workers"


class TestParallelStatsEdgeCases:
    """Test edge cases for parallel statistics."""
    
    def test_parallel_stats_empty_column_list(self, weather_analyzer):
        """Parallel stats with empty column list should return empty list."""
        results = weather_analyzer.descriptive_stats_parallel([])
        assert results == [], "Should return empty list for empty columns"
    
    def test_parallel_stats_single_worker(self, weather_analyzer):
        """Parallel stats with 1 worker should work (essentially serial)."""
        column = "Rainfall"
        results = weather_analyzer.descriptive_stats_parallel([column], workers=1)
        assert len(results) == 1, "Should return result with 1 worker"
    
    def test_parallel_stats_many_workers(self, weather_analyzer, numeric_columns):
        """Parallel stats should handle more workers than columns."""
        results = weather_analyzer.descriptive_stats_parallel(numeric_columns, workers=16)
        assert len(results) == len(numeric_columns), "Should work even with excess workers"


class TestParallelStatsIntegration:
    """Integration tests for parallel statistics."""
    
    def test_parallel_stats_complete_workflow(self, csv_file):
        """Test complete workflow: load data and compute parallel stats."""
        df = load_weather_csv(csv_file)
        store = WeatherDataStore(df)
        analyzer = WeatherAnalyzer(store)
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()[:3]
        results = analyzer.descriptive_stats_parallel(numeric_cols, workers=2)
        
        assert len(results) == len(numeric_cols), "Should compute for all specified columns"
        assert all("column" in r for r in results), "Each result should have a column field"
