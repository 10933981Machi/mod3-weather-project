"""
spark_weather.py

PySpark-based weather data processing and analysis.
Migrates the pandas-based weatherstats functionality to run on a Spark cluster,
demonstrating distributed data processing with PySpark DataFrames and SQL.

This module provides:
- SparkSession creation and configuration
- CSV loading into Spark DataFrames
- Descriptive statistics using Spark aggregation functions
- Data filtering and transformation using Spark operations
- GroupBy aggregations for location and time-based analysis
"""

import os
import logging
from pathlib import Path

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType

logger = logging.getLogger(__name__)

# Candidate Java 17 installations in order of preference.
# PySpark 4.x is incompatible with Java 21+ Hadoop Subject API changes.
_JAVA17_CANDIDATES = [
    "/usr/local/sdkman/candidates/java/17.0.18-amzn",
    "/usr/lib/jvm/java-17-openjdk-amd64",
    "/usr/lib/jvm/java-17-openjdk",
]


def _ensure_java17() -> None:
    """
    Point JAVA_HOME at Java 17 before the JVM starts.

    PySpark 4.x bundles Hadoop code that calls javax.security.auth.Subject.getSubject(),
    which was removed in Java 21. Running under Java 17 avoids the UnsupportedOperationException.
    If Java 17 is already active this is a no-op.
    """
    current_home = os.environ.get("JAVA_HOME", "")
    if "17" in current_home:
        return  # already pointing at Java 17

    for candidate in _JAVA17_CANDIDATES:
        p = Path(candidate)
        if p.exists() and (p / "bin" / "java").exists():
            os.environ["JAVA_HOME"] = str(p)
            os.environ["PATH"] = str(p / "bin") + ":" + os.environ.get("PATH", "")
            logger.debug(f"Set JAVA_HOME to {p} for PySpark compatibility")
            return


def create_spark_session(app_name: str = "WeatherStats") -> SparkSession:
    """
    Create and return a local SparkSession for weather data analysis.

    Uses local[*] master to utilize all available CPU cores,
    simulating a cluster environment on a single machine.

    Args:
        app_name: Name for the Spark application.

    Returns:
        A configured SparkSession instance.
    """
    # Must run before the JVM starts — fixes UnsupportedOperationException
    # caused by Hadoop's Subject.getSubject() removal in Java 21+.
    _ensure_java17()

    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )
    # reduce noisy Spark log output
    spark.sparkContext.setLogLevel("WARN")
    logger.info(f"SparkSession created: {app_name}")
    return spark


def load_weather_csv_spark(spark: SparkSession, csv_path: str | Path) -> DataFrame:
    """
    Load a weather CSV file into a Spark DataFrame.

    Reads the CSV with header inference and schema inference enabled,
    distributing the data across Spark partitions for parallel processing.

    Args:
        spark: Active SparkSession.
        csv_path: Path to the CSV file.

    Returns:
        A Spark DataFrame containing the weather dataset.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    logger.info(f"Loading CSV into Spark DataFrame: {csv_path}")
    sdf = spark.read.csv(
        str(csv_path),
        header=True,
        inferSchema=True,
    )
    row_count = sdf.count()
    logger.info(f"Loaded {row_count} rows, {len(sdf.columns)} columns into Spark")
    return sdf


def descriptive_stats_spark(sdf: DataFrame, column: str) -> dict:
    """
    Compute descriptive statistics for a numeric column using Spark.

    Calculates count, mean, median, min, max, range, std, and variance
    entirely within the Spark engine using built-in aggregation functions.

    Args:
        sdf: Spark DataFrame containing the dataset.
        column: Name of the numeric column to analyze.

    Returns:
        Dictionary with computed statistics, or an error entry if the column
        is missing or has no valid numeric values.
    """
    if column not in sdf.columns:
        return {"column": column, "error": "Column not found"}

    # cast to double to handle any string columns
    col_df = sdf.select(F.col(column).cast(DoubleType()).alias(column)).na.drop()

    count_val = col_df.count()
    if count_val == 0:
        return {"column": column, "error": "No valid numeric values found"}

    # compute aggregates in a single pass over the data
    agg_result = col_df.agg(
        F.count(column).alias("count"),
        F.mean(column).alias("mean"),
        F.min(column).alias("min"),
        F.max(column).alias("max"),
        F.stddev(column).alias("std"),
        F.variance(column).alias("var"),
    ).collect()[0]

    # median requires approx or exact percentile
    median_val = col_df.approxQuantile(column, [0.5], 0.001)[0]

    # mode: most frequent value
    mode_row = (
        col_df.groupBy(column)
        .count()
        .orderBy(F.desc("count"))
        .first()
    )
    mode_val = float(mode_row[column]) if mode_row else None

    return {
        "column": column,
        "count": int(agg_result["count"]),
        "mean": float(agg_result["mean"]),
        "median": float(median_val),
        "mode": mode_val,
        "min": float(agg_result["min"]),
        "max": float(agg_result["max"]),
        "range": float(agg_result["max"] - agg_result["min"]),
        "std": float(agg_result["std"]),
        "var": float(agg_result["var"]),
    }


def descriptive_stats_all_spark(sdf: DataFrame, columns: list[str] | None = None) -> list[dict]:
    """
    Compute descriptive statistics for multiple columns using Spark.

    Iterates over the specified columns and computes stats for each one.
    Spark handles the parallelism internally across its cluster partitions.

    Args:
        sdf: Spark DataFrame.
        columns: List of column names. If None, uses all columns.

    Returns:
        List of stat dictionaries, one per column.
    """
    if columns is None:
        columns = sdf.columns

    results = []
    for col in columns:
        stats = descriptive_stats_spark(sdf, col)
        results.append(stats)
    return results


def filter_rainy_days_spark(sdf: DataFrame) -> DataFrame:
    """
    Filter the DataFrame to only include rows where Rainfall > 0.

    Uses Spark's distributed filter operation which runs across all
    partitions in parallel.

    Args:
        sdf: Spark DataFrame with a 'Rainfall' column.

    Returns:
        Filtered Spark DataFrame containing only rainy day records.
    """
    return sdf.filter(
        F.col("Rainfall").cast(DoubleType()).isNotNull()
        & (F.col("Rainfall").cast(DoubleType()) > 0)
    )


def total_rainfall_spark(sdf: DataFrame) -> float:
    """
    Compute total rainfall across the entire dataset using Spark aggregation.

    Equivalent to the pandas reduce-based approach, but executed in parallel
    across Spark partitions.

    Args:
        sdf: Spark DataFrame with a 'Rainfall' column.

    Returns:
        Total rainfall as a float.
    """
    result = sdf.agg(
        F.sum(F.col("Rainfall").cast(DoubleType())).alias("total")
    ).collect()[0]["total"]
    return float(result) if result is not None else 0.0


def high_temperature_days_spark(sdf: DataFrame, threshold: float = 35.0) -> DataFrame:
    """
    Filter records where MaxTemp meets or exceeds the given threshold.

    Args:
        sdf: Spark DataFrame with a 'MaxTemp' column.
        threshold: Minimum temperature to include (default 35.0 C).

    Returns:
        Filtered Spark DataFrame.
    """
    return sdf.filter(
        F.col("MaxTemp").cast(DoubleType()).isNotNull()
        & (F.col("MaxTemp").cast(DoubleType()) >= threshold)
    )


def avg_temp_by_location_spark(sdf: DataFrame) -> DataFrame:
    """
    Compute average MinTemp and MaxTemp grouped by Location using Spark.

    Demonstrates Spark's groupBy + agg pattern for distributed aggregation.

    Args:
        sdf: Spark DataFrame with Location, MinTemp, MaxTemp columns.

    Returns:
        Spark DataFrame with columns: Location, avg_min_temp, avg_max_temp.
    """
    return (
        sdf.groupBy("Location")
        .agg(
            F.avg(F.col("MinTemp").cast(DoubleType())).alias("avg_min_temp"),
            F.avg(F.col("MaxTemp").cast(DoubleType())).alias("avg_max_temp"),
        )
        .orderBy(F.desc("avg_max_temp"))
    )


def avg_rainfall_by_location_spark(sdf: DataFrame) -> DataFrame:
    """
    Compute average rainfall grouped by Location using Spark.

    Args:
        sdf: Spark DataFrame with Location and Rainfall columns.

    Returns:
        Spark DataFrame with columns: Location, avg_rainfall, sorted descending.
    """
    return (
        sdf.groupBy("Location")
        .agg(
            F.avg(F.col("Rainfall").cast(DoubleType())).alias("avg_rainfall"),
        )
        .orderBy(F.desc("avg_rainfall"))
    )


def rain_today_counts_spark(sdf: DataFrame) -> DataFrame:
    """
    Count occurrences of each RainToday value using Spark.

    Demonstrates distributed counting/grouping operations.

    Args:
        sdf: Spark DataFrame with a 'RainToday' column.

    Returns:
        Spark DataFrame with columns: RainToday, count.
    """
    return (
        sdf.groupBy("RainToday")
        .count()
        .orderBy(F.desc("count"))
    )


def spark_sql_analysis(spark: SparkSession, sdf: DataFrame) -> dict:
    """
    Perform weather analysis using Spark SQL queries.

    Registers the DataFrame as a temporary SQL view and runs SQL queries
    against it, demonstrating Spark's SQL interface for data analysis.

    Args:
        spark: Active SparkSession.
        sdf: Spark DataFrame to register as a SQL table.

    Returns:
        Dictionary with keys mapping to query result DataFrames.
    """
    sdf.createOrReplaceTempView("weather")

    # 1) Top 10 hottest locations by average MaxTemp
    hottest = spark.sql("""
        SELECT Location,
               ROUND(AVG(CAST(MaxTemp AS DOUBLE)), 2) AS avg_max_temp,
               COUNT(*) AS record_count
        FROM weather
        WHERE MaxTemp IS NOT NULL
        GROUP BY Location
        ORDER BY avg_max_temp DESC
        LIMIT 10
    """)

    # 2) Top 10 wettest locations by average Rainfall
    wettest = spark.sql("""
        SELECT Location,
               ROUND(AVG(CAST(Rainfall AS DOUBLE)), 2) AS avg_rainfall,
               COUNT(*) AS record_count
        FROM weather
        WHERE Rainfall IS NOT NULL
        GROUP BY Location
        ORDER BY avg_rainfall DESC
        LIMIT 10
    """)

    # 3) Overall weather summary
    summary = spark.sql("""
        SELECT
            COUNT(*) AS total_records,
            ROUND(AVG(CAST(MinTemp AS DOUBLE)), 2) AS avg_min_temp,
            ROUND(AVG(CAST(MaxTemp AS DOUBLE)), 2) AS avg_max_temp,
            ROUND(SUM(CAST(Rainfall AS DOUBLE)), 2) AS total_rainfall,
            ROUND(AVG(CAST(Humidity9am AS DOUBLE)), 2) AS avg_humidity_9am,
            ROUND(AVG(CAST(Humidity3pm AS DOUBLE)), 2) AS avg_humidity_3pm
        FROM weather
    """)

    # 4) Rain distribution
    rain_dist = spark.sql("""
        SELECT RainToday,
               COUNT(*) AS count,
               ROUND(AVG(CAST(Rainfall AS DOUBLE)), 2) AS avg_rainfall
        FROM weather
        GROUP BY RainToday
        ORDER BY count DESC
    """)

    return {
        "hottest_locations": hottest,
        "wettest_locations": wettest,
        "overall_summary": summary,
        "rain_distribution": rain_dist,
    }
