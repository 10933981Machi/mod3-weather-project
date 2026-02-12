"""
test_weatherstats.py

Unit tests for the weatherstats module.
Tests all classes and functions from Module 4:
- load_weather_csv() function
- weather_records_generator() function
- WeatherDataStore class
- WeatherAnalyzer class
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Add src to path
project_root = Path(__file__).resolve().parents[1]
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from weatherstats import (
    load_weather_csv,
    weather_records_generator,
    WeatherDataStore,
    WeatherAnalyzer
)


# TESTS FOR load_weather_csv() FUNCTION

class TestLoadWeatherCsv:
    """Unit tests for load_weather_csv() function from io.py"""

    def test_load_weather_csv_returns_dataframe(self, csv_training_path):
        """Test that load_weather_csv returns a pandas DataFrame."""
        df = load_weather_csv(csv_training_path)
        assert isinstance(df, pd.DataFrame)

    def test_load_weather_csv_has_data(self, csv_training_path):
        """Test that loaded CSV has data (non-empty)."""
        df = load_weather_csv(csv_training_path)
        assert len(df) > 0
        assert len(df.columns) > 0

    def test_load_weather_csv_training_data_size(self, csv_training_path):
        """Test that training data has expected size (99,516 rows)."""
        df = load_weather_csv(csv_training_path)
        assert len(df) == 99516
        assert len(df.columns) >= 1

    def test_load_weather_csv_test_data_loads(self, csv_test_path):
        """Test that test CSV file loads successfully."""
        df = load_weather_csv(csv_test_path)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_load_weather_csv_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_weather_csv("/nonexistent/path/file.csv")

    def test_load_weather_csv_has_columns(self, csv_training_path):
        """Test that loaded data has column names."""
        df = load_weather_csv(csv_training_path)
        assert list(df.columns) is not None
        assert len(df.columns) > 0


# TESTS FOR weather_records_generator() FUNCTION


class TestWeatherRecordsGenerator:
    """Unit tests for weather_records_generator() function from io.py"""

    def test_weather_records_generator_is_generator(self, csv_training_path):
        """Test that weather_records_generator returns a generator."""
        gen = weather_records_generator(csv_training_path)
        assert hasattr(gen, '__iter__')
        assert hasattr(gen, '__next__')

    def test_weather_records_generator_yields_dicts(self, csv_training_path):
        """Test that generator yields dictionaries."""
        gen = weather_records_generator(csv_training_path)
        first_record = next(gen)
        assert isinstance(first_record, dict)

    def test_weather_records_generator_yields_data(self, csv_training_path):
        """Test that generator yields non-empty records."""
        gen = weather_records_generator(csv_training_path)
        first_record = next(gen)
        assert len(first_record) > 0

    def test_weather_records_generator_multiple_records(self, csv_training_path):
        """Test that generator yields multiple records."""
        gen = weather_records_generator(csv_training_path)
        records = []
        for i, record in enumerate(gen):
            records.append(record)
            if i >= 4:  # Get 5 records
                break
        assert len(records) == 5

    def test_weather_records_generator_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent file."""
        with pytest.raises(FileNotFoundError):
            gen = weather_records_generator("/nonexistent/path/file.csv")
            next(gen)

    def test_weather_records_generator_records_are_dicts(self, csv_training_path):
        """Test that all records yielded by generator are dictionaries."""
        gen = weather_records_generator(csv_training_path)
        for i, record in enumerate(gen):
            assert isinstance(record, dict)
            if i >= 9:  # Check first 10 records
                break


# TESTS FOR WeatherDataStore CLASS

class TestWeatherDataStore:
    """Unit tests for WeatherDataStore class from stats.py"""

    def test_weather_data_store_init(self, training_dataframe):
        """Test that WeatherDataStore initializes with a DataFrame."""
        store = WeatherDataStore(training_dataframe)
        assert isinstance(store, WeatherDataStore)

    def test_weather_data_store_get_dataframe(self, weather_store, training_dataframe):
        """Test that get_dataframe returns the stored DataFrame."""
        df = weather_store.get_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert df.equals(training_dataframe)

    def test_weather_data_store_len(self, weather_store, training_dataframe):
        """Test that __len__ returns correct number of rows."""
        assert len(weather_store) == len(training_dataframe)

    def test_weather_data_store_len_is_99516(self, weather_store):
        """Test that store contains 99,516 rows from training data."""
        assert len(weather_store) == 99516

    def test_weather_data_store_is_iterable(self, weather_store):
        """Test that WeatherDataStore is iterable."""
        assert hasattr(weather_store, '__iter__')

    def test_weather_data_store_iterator_yields_dicts(self, weather_store):
        """Test that iterator yields dictionaries."""
        first_record = next(iter(weather_store))
        assert isinstance(first_record, dict)

    def test_weather_data_store_iterate_multiple_records(self, weather_store):
        """Test that iterator can yield multiple records."""
        records = []
        for i, record in enumerate(weather_store):
            records.append(record)
            if i >= 4:  # Get 5 records
                break
        assert len(records) == 5
        assert all(isinstance(r, dict) for r in records)

    def test_weather_data_store_iterate_all_records(self, weather_store, training_dataframe):
        """Test that iterator yields all records."""
        count = 0
        for _ in weather_store:
            count += 1
        assert count == len(training_dataframe)


# TESTS FOR WeatherAnalyzer CLASS

class TestWeatherAnalyzer:
    """Unit tests for WeatherAnalyzer class from stats.py"""

    def test_weather_analyzer_init(self, weather_store):
        """Test that WeatherAnalyzer initializes with a store."""
        analyzer = WeatherAnalyzer(weather_store)
        assert isinstance(analyzer, WeatherAnalyzer)

    def test_descriptive_stats_returns_dict(self, weather_analyzer):
        """Test that descriptive_stats returns a dictionary."""
        stats = weather_analyzer.descriptive_stats("MinTemp")
        assert isinstance(stats, dict)

    def test_descriptive_stats_has_required_keys(self, weather_analyzer):
        """Test that stats dict has all required statistical keys."""
        stats = weather_analyzer.descriptive_stats("MinTemp")
        required_keys = ["column", "count", "mean", "median", "mode", "min", "max", "range", "std", "var"]
        for key in required_keys:
            assert key in stats

    def test_descriptive_stats_mean_numeric(self, weather_analyzer):
        """Test that mean is a numeric value."""
        stats = weather_analyzer.descriptive_stats("MinTemp")
        assert isinstance(stats["mean"], (int, float))

    def test_descriptive_stats_median_numeric(self, weather_analyzer):
        """Test that median is a numeric value."""
        stats = weather_analyzer.descriptive_stats("MinTemp")
        assert isinstance(stats["median"], (int, float))

    def test_descriptive_stats_count_positive(self, weather_analyzer):
        """Test that count is a positive integer."""
        stats = weather_analyzer.descriptive_stats("MinTemp")
        assert isinstance(stats["count"], int)
        assert stats["count"] > 0

    def test_descriptive_stats_min_max_valid(self, weather_analyzer):
        """Test that min and max are valid numbers."""
        stats = weather_analyzer.descriptive_stats("MinTemp")
        assert isinstance(stats["min"], (int, float))
        assert isinstance(stats["max"], (int, float))
        assert stats["min"] <= stats["max"]

    def test_descriptive_stats_range_valid(self, weather_analyzer):
        """Test that range equals max - min."""
        stats = weather_analyzer.descriptive_stats("MinTemp")
        expected_range = stats["max"] - stats["min"]
        assert stats["range"] == expected_range

    def test_descriptive_stats_std_variance_numeric(self, weather_analyzer):
        """Test that std and variance are numeric values."""
        stats = weather_analyzer.descriptive_stats("MinTemp")
        assert isinstance(stats["std"], (int, float))
        assert isinstance(stats["var"], (int, float))

    def test_descriptive_stats_invalid_column(self, weather_analyzer):
        """Test that invalid column returns error dict."""
        stats = weather_analyzer.descriptive_stats("NonExistentColumn")
        assert "error" in stats
        assert stats["error"] == "Column not found"

    def test_descriptive_stats_max_temp(self, weather_analyzer):
        """Test descriptive_stats with MaxTemp column."""
        stats = weather_analyzer.descriptive_stats("MaxTemp")
        assert stats["column"] == "MaxTemp"
        assert "error" not in stats
        assert stats["count"] > 0

    def test_descriptive_stats_rainfall(self, weather_analyzer):
        """Test descriptive_stats with Rainfall column."""
        stats = weather_analyzer.descriptive_stats("Rainfall")
        assert stats["column"] == "Rainfall"
        assert "error" not in stats
        assert stats["count"] > 0

    def test_descriptive_stats_multiple_columns(self, weather_analyzer):
        """Test descriptive_stats with multiple different columns."""
        columns = ["MinTemp", "MaxTemp", "Rainfall"]
        for col in columns:
            stats = weather_analyzer.descriptive_stats(col)
            assert "error" not in stats
            assert stats["column"] == col


# INTEGRATION TESTS

class TestIntegration:
    """Integration tests combining multiple components."""

    def test_load_and_store(self, csv_training_path):
        """Test loading CSV and creating store."""
        df = load_weather_csv(csv_training_path)
        store = WeatherDataStore(df)
        assert len(store) == 99516

    def test_load_store_and_analyze(self, csv_training_path):
        """Test full workflow: load, store, analyze."""
        df = load_weather_csv(csv_training_path)
        store = WeatherDataStore(df)
        analyzer = WeatherAnalyzer(store)
        stats = analyzer.descriptive_stats("MinTemp")
        assert "error" not in stats
        assert stats["count"] > 0

    def test_generator_with_store(self, csv_training_path):
        """Test generator function works independently."""
        gen = weather_records_generator(csv_training_path)
        records = [next(gen) for _ in range(3)]
        assert len(records) == 3
        assert all(isinstance(r, dict) for r in records)

    def test_store_iteration_consistency(self, weather_store, training_dataframe):
        """Test that store iteration is consistent with DataFrame."""
        store_length = len(weather_store)
        df_length = len(training_dataframe)
        assert store_length == df_length
