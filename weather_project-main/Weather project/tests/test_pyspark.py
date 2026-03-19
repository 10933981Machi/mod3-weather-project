"""
test_pyspark.py

Tests for the PySpark weather data processing module.
Verifies that the Spark-based analysis produces correct and consistent
results compared to the pandas-based implementation.

Covers:
- SparkSession creation
- CSV loading into Spark DataFrames
- Descriptive statistics accuracy
- Filtering operations (rainy days, high temp days)
- Aggregation operations (total rainfall, averages by location)
- Spark SQL query execution
- Edge cases and error handling
"""

import sys
from pathlib import Path

import pytest
import pandas as pd

# add src to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

from weatherstats.spark_weather import (
    create_spark_session,
    load_weather_csv_spark,
    descriptive_stats_spark,
    descriptive_stats_all_spark,
    filter_rainy_days_spark,
    total_rainfall_spark,
    high_temperature_days_spark,
    avg_temp_by_location_spark,
    avg_rainfall_by_location_spark,
    rain_today_counts_spark,
    spark_sql_analysis,
)
from weatherstats.io import load_weather_csv
from weatherstats.stats import WeatherDataStore, WeatherAnalyzer


# ---- Fixtures ----

@pytest.fixture(scope="module")
def spark():
    """Create a single SparkSession shared across all tests in this module."""
    session = create_spark_session("WeatherStats-Test")
    yield session
    session.stop()


@pytest.fixture(scope="module")
def csv_path():
    """Path to the training CSV file."""
    return project_root / "Data" / "Weather Training Data.csv"


@pytest.fixture(scope="module")
def spark_df(spark, csv_path):
    """Spark DataFrame loaded from training CSV."""
    return load_weather_csv_spark(spark, csv_path)


@pytest.fixture(scope="module")
def pandas_df(csv_path):
    """Pandas DataFrame loaded from training CSV for comparison."""
    return load_weather_csv(csv_path)


# ---- Test SparkSession Creation ----

class TestSparkSession:
    """Tests for SparkSession creation and configuration."""

    def test_session_created(self, spark):
        """SparkSession should be active and usable."""
        assert spark is not None
        assert spark.sparkContext is not None

    def test_session_app_name(self, spark):
        """App name should match what was requested."""
        assert spark.sparkContext.appName == "WeatherStats-Test"

    def test_session_local_master(self, spark):
        """Should be running in local mode."""
        assert "local" in spark.sparkContext.master


# ---- Test CSV Loading ----

class TestLoadCSV:
    """Tests for loading CSV data into Spark DataFrames."""

    def test_load_returns_dataframe(self, spark_df):
        """Should return a Spark DataFrame."""
        from pyspark.sql import DataFrame
        assert isinstance(spark_df, DataFrame)

    def test_row_count_matches_pandas(self, spark_df, pandas_df):
        """Spark row count should match pandas row count."""
        assert spark_df.count() == len(pandas_df)

    def test_column_count_matches(self, spark_df, pandas_df):
        """Spark column count should match pandas column count."""
        assert len(spark_df.columns) == len(pandas_df.columns)

    def test_columns_present(self, spark_df):
        """Key weather columns should be present."""
        expected = ["Location", "MinTemp", "MaxTemp", "Rainfall", "RainToday"]
        for col in expected:
            assert col in spark_df.columns, f"Missing column: {col}"

    def test_file_not_found(self, spark):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_weather_csv_spark(spark, "/nonexistent/path.csv")


# ---- Test Descriptive Statistics ----

class TestDescriptiveStats:
    """Tests for Spark-based descriptive statistics."""

    def test_stats_returns_dict(self, spark_df):
        """Should return a dictionary of statistics."""
        stats = descriptive_stats_spark(spark_df, "MaxTemp")
        assert isinstance(stats, dict)

    def test_stats_has_all_keys(self, spark_df):
        """Result should contain all expected stat keys."""
        stats = descriptive_stats_spark(spark_df, "MaxTemp")
        expected_keys = ["column", "count", "mean", "median", "mode",
                         "min", "max", "range", "std", "var"]
        for key in expected_keys:
            assert key in stats, f"Missing key: {key}"

    def test_stats_count_matches_pandas(self, spark_df, pandas_df):
        """Count of valid values should match pandas."""
        spark_stats = descriptive_stats_spark(spark_df, "MaxTemp")
        pandas_count = pd.to_numeric(pandas_df["MaxTemp"], errors="coerce").dropna().count()
        assert spark_stats["count"] == pandas_count

    def test_stats_mean_close_to_pandas(self, spark_df, pandas_df):
        """Mean should be close to pandas mean (within tolerance)."""
        spark_stats = descriptive_stats_spark(spark_df, "MaxTemp")
        pandas_mean = pd.to_numeric(pandas_df["MaxTemp"], errors="coerce").dropna().mean()
        assert abs(spark_stats["mean"] - pandas_mean) < 0.01

    def test_stats_min_max_match(self, spark_df, pandas_df):
        """Min/max should match pandas exactly."""
        spark_stats = descriptive_stats_spark(spark_df, "MaxTemp")
        series = pd.to_numeric(pandas_df["MaxTemp"], errors="coerce").dropna()
        assert abs(spark_stats["min"] - series.min()) < 0.01
        assert abs(spark_stats["max"] - series.max()) < 0.01

    def test_stats_invalid_column(self, spark_df):
        """Should return error for nonexistent column."""
        stats = descriptive_stats_spark(spark_df, "FakeColumn")
        assert "error" in stats

    def test_stats_multiple_columns(self, spark_df):
        """Should compute stats for multiple columns."""
        results = descriptive_stats_all_spark(spark_df, ["MinTemp", "MaxTemp", "Rainfall"])
        assert len(results) == 3
        for r in results:
            assert "column" in r


# ---- Test Filtering Operations ----

class TestFiltering:
    """Tests for Spark-based filtering operations."""

    def test_rainy_days_count(self, spark_df, pandas_df):
        """Rainy day count should be reasonable."""
        rainy = filter_rainy_days_spark(spark_df)
        rainy_count = rainy.count()
        # should be fewer than total records
        assert rainy_count < spark_df.count()
        assert rainy_count > 0

    def test_rainy_days_all_positive(self, spark_df):
        """All filtered records should have Rainfall > 0."""
        rainy = filter_rainy_days_spark(spark_df)
        # check that min rainfall in filtered set is > 0
        from pyspark.sql import functions as F
        from pyspark.sql.types import DoubleType
        min_rain = rainy.agg(
            F.min(F.col("Rainfall").cast(DoubleType()))
        ).collect()[0][0]
        assert min_rain > 0

    def test_high_temp_days(self, spark_df):
        """High temp filter should return records >= threshold."""
        hot = high_temperature_days_spark(spark_df, threshold=35.0)
        assert hot.count() > 0
        assert hot.count() < spark_df.count()

    def test_high_temp_days_custom_threshold(self, spark_df):
        """Custom threshold should change the result count."""
        hot_35 = high_temperature_days_spark(spark_df, threshold=35.0)
        hot_40 = high_temperature_days_spark(spark_df, threshold=40.0)
        # higher threshold should return fewer records
        assert hot_40.count() <= hot_35.count()


# ---- Test Aggregations ----

class TestAggregations:
    """Tests for Spark-based aggregation operations."""

    def test_total_rainfall_positive(self, spark_df):
        """Total rainfall should be a positive number."""
        total = total_rainfall_spark(spark_df)
        assert total > 0

    def test_total_rainfall_close_to_pandas(self, spark_df, pandas_df):
        """Spark total rainfall should be close to pandas sum."""
        spark_total = total_rainfall_spark(spark_df)
        pandas_total = pd.to_numeric(pandas_df["Rainfall"], errors="coerce").sum()
        # allow small floating point differences
        assert abs(spark_total - pandas_total) < 1.0

    def test_avg_temp_by_location(self, spark_df):
        """Average temp by location should return results."""
        result = avg_temp_by_location_spark(spark_df)
        count = result.count()
        assert count > 0
        assert "avg_min_temp" in result.columns
        assert "avg_max_temp" in result.columns

    def test_avg_rainfall_by_location(self, spark_df):
        """Average rainfall by location should return results."""
        result = avg_rainfall_by_location_spark(spark_df)
        count = result.count()
        assert count > 0
        assert "avg_rainfall" in result.columns

    def test_rain_today_counts(self, spark_df):
        """RainToday counts should have expected categories."""
        result = rain_today_counts_spark(spark_df)
        count = result.count()
        # should have at least "Yes" and "No"
        assert count >= 2


# ---- Test Spark SQL ----

class TestSparkSQL:
    """Tests for Spark SQL query execution."""

    def test_sql_returns_dict(self, spark, spark_df):
        """spark_sql_analysis should return a dictionary."""
        results = spark_sql_analysis(spark, spark_df)
        assert isinstance(results, dict)

    def test_sql_has_all_keys(self, spark, spark_df):
        """Result should contain all expected query keys."""
        results = spark_sql_analysis(spark, spark_df)
        expected = ["hottest_locations", "wettest_locations",
                    "overall_summary", "rain_distribution"]
        for key in expected:
            assert key in results

    def test_hottest_locations_count(self, spark, spark_df):
        """Should return up to 10 hottest locations."""
        results = spark_sql_analysis(spark, spark_df)
        count = results["hottest_locations"].count()
        assert 0 < count <= 10

    def test_overall_summary_has_values(self, spark, spark_df):
        """Overall summary should have non-null aggregate values."""
        results = spark_sql_analysis(spark, spark_df)
        summary_row = results["overall_summary"].collect()[0]
        assert summary_row["total_records"] > 0
        assert summary_row["avg_max_temp"] is not None
        assert summary_row["total_rainfall"] is not None


# ---- Test Parity with Pandas ----

class TestPandasParity:
    """Verify Spark results match pandas-based results within tolerance."""

    def test_mintemp_stats_parity(self, spark_df, pandas_df):
        """MinTemp stats from Spark should match pandas within tolerance."""
        spark_stats = descriptive_stats_spark(spark_df, "MinTemp")

        store = WeatherDataStore(pandas_df)
        analyzer = WeatherAnalyzer(store)
        pandas_stats = analyzer.descriptive_stats("MinTemp")

        assert abs(spark_stats["mean"] - pandas_stats["mean"]) < 0.1
        assert abs(spark_stats["min"] - pandas_stats["min"]) < 0.01
        assert abs(spark_stats["max"] - pandas_stats["max"]) < 0.01
        assert spark_stats["count"] == pandas_stats["count"]

    def test_maxtemp_stats_parity(self, spark_df, pandas_df):
        """MaxTemp stats from Spark should match pandas within tolerance."""
        spark_stats = descriptive_stats_spark(spark_df, "MaxTemp")

        store = WeatherDataStore(pandas_df)
        analyzer = WeatherAnalyzer(store)
        pandas_stats = analyzer.descriptive_stats("MaxTemp")

        assert abs(spark_stats["mean"] - pandas_stats["mean"]) < 0.1
        assert abs(spark_stats["min"] - pandas_stats["min"]) < 0.01
        assert abs(spark_stats["max"] - pandas_stats["max"]) < 0.01

    def test_rainfall_stats_parity(self, spark_df, pandas_df):
        """Rainfall stats from Spark should match pandas within tolerance."""
        spark_stats = descriptive_stats_spark(spark_df, "Rainfall")

        store = WeatherDataStore(pandas_df)
        analyzer = WeatherAnalyzer(store)
        pandas_stats = analyzer.descriptive_stats("Rainfall")

        assert abs(spark_stats["mean"] - pandas_stats["mean"]) < 0.1
        assert abs(spark_stats["min"] - pandas_stats["min"]) < 0.01
        assert abs(spark_stats["max"] - pandas_stats["max"]) < 0.01
