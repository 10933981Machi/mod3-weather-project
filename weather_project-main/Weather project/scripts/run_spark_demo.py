#!/usr/bin/env python3
"""
run_spark_demo.py

Demonstrates the PySpark migration of the weather statistics application.
Loads weather data into Spark DataFrames and performs distributed analysis
including descriptive statistics, filtering, aggregations, and SQL queries.

Run from the Weather project folder:
    python3 scripts/run_spark_demo.py
"""

import sys
from pathlib import Path

# add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

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


def main():
    project_root = Path(__file__).resolve().parents[1]
    csv_path = project_root / "Data" / "Weather Training Data.csv"

    print("\n" + "=" * 65)
    print("  WEATHER STATS - Module 8: PySpark Cluster Migration")
    print("=" * 65)

    # ---- 1. Create Spark Session ----
    print("\n[1] Creating SparkSession (local[*] mode) ...")
    spark = create_spark_session("WeatherStats-Demo")
    print(f"    Spark version : {spark.version}")
    print(f"    Master        : {spark.sparkContext.master}")
    print(f"    App name      : {spark.sparkContext.appName}")

    # ---- 2. Load CSV into Spark DataFrame ----
    print("\n[2] Loading CSV into Spark DataFrame ...")
    sdf = load_weather_csv_spark(spark, csv_path)
    print(f"    Rows    : {sdf.count()}")
    print(f"    Columns : {len(sdf.columns)}")
    print(f"    Partitions : {sdf.rdd.getNumPartitions()}")
    print("\n    Schema:")
    sdf.printSchema()

    print("    First 5 rows:")
    sdf.show(5, truncate=True)

    # ---- 3. Descriptive Statistics (Spark) ----
    print("\n[3] Descriptive Statistics via Spark aggregation functions")
    print("-" * 65)
    numeric_cols = ["MinTemp", "MaxTemp", "Rainfall"]
    for col in numeric_cols:
        stats = descriptive_stats_spark(sdf, col)
        if "error" in stats:
            print(f"    {col}: ERROR - {stats['error']}")
        else:
            print(f"    {col}:")
            print(f"      Count  = {stats['count']}")
            print(f"      Mean   = {stats['mean']:.2f}")
            print(f"      Median = {stats['median']:.2f}")
            print(f"      Mode   = {stats['mode']}")
            print(f"      Min    = {stats['min']:.2f}")
            print(f"      Max    = {stats['max']:.2f}")
            print(f"      Range  = {stats['range']:.2f}")
            print(f"      Std    = {stats['std']:.2f}")
            print(f"      Var    = {stats['var']:.2f}")

    # ---- 4. Spark built-in describe() ----
    print("\n[4] Spark describe() for numeric overview")
    print("-" * 65)
    sdf.select("MinTemp", "MaxTemp", "Rainfall", "Humidity9am", "Humidity3pm").describe().show()

    # ---- 5. Filtering - Rainy Days ----
    print("\n[5] Filtering: Rainy days (Rainfall > 0)")
    print("-" * 65)
    rainy = filter_rainy_days_spark(sdf)
    print(f"    Total records    : {sdf.count()}")
    print(f"    Rainy day records: {rainy.count()}")
    print(f"    Sample rainy days:")
    rainy.select("Location", "MinTemp", "MaxTemp", "Rainfall").show(5, truncate=False)

    # ---- 6. Total Rainfall ----
    print("\n[6] Total Rainfall (Spark aggregation)")
    print("-" * 65)
    total = total_rainfall_spark(sdf)
    print(f"    Total rainfall across dataset: {total:.2f} mm")

    # ---- 7. High Temperature Days ----
    print("\n[7] High Temperature Days (MaxTemp >= 35 C)")
    print("-" * 65)
    hot = high_temperature_days_spark(sdf)
    print(f"    Records with MaxTemp >= 35: {hot.count()}")
    hot.select("Location", "MaxTemp", "Rainfall").show(5, truncate=False)

    # ---- 8. Average Temp by Location ----
    print("\n[8] Average Temperature by Location (Top 10)")
    print("-" * 65)
    avg_temps = avg_temp_by_location_spark(sdf)
    avg_temps.show(10, truncate=False)

    # ---- 9. Average Rainfall by Location ----
    print("\n[9] Average Rainfall by Location (Top 10)")
    print("-" * 65)
    avg_rain = avg_rainfall_by_location_spark(sdf)
    avg_rain.show(10, truncate=False)

    # ---- 10. RainToday Distribution ----
    print("\n[10] RainToday Counts")
    print("-" * 65)
    rain_counts = rain_today_counts_spark(sdf)
    rain_counts.show()

    # ---- 11. Spark SQL Analysis ----
    print("\n[11] Spark SQL Queries")
    print("-" * 65)
    sql_results = spark_sql_analysis(spark, sdf)

    print("\n    Top 10 Hottest Locations (by avg MaxTemp):")
    sql_results["hottest_locations"].show(10, truncate=False)

    print("    Top 10 Wettest Locations (by avg Rainfall):")
    sql_results["wettest_locations"].show(10, truncate=False)

    print("    Overall Weather Summary:")
    sql_results["overall_summary"].show(truncate=False)

    print("    Rain Distribution:")
    sql_results["rain_distribution"].show(truncate=False)

    # ---- 12. Multi-column stats ----
    print("\n[12] Multi-column Descriptive Stats")
    print("-" * 65)
    all_stats = descriptive_stats_all_spark(sdf, ["WindGustSpeed", "Humidity9am", "Pressure9am"])
    for s in all_stats:
        if "error" not in s:
            print(f"    {s['column']}: mean={s['mean']:.2f}, std={s['std']:.2f}, range={s['range']:.2f}")
        else:
            print(f"    {s['column']}: {s['error']}")

    # ---- Done ----
    print("\n" + "=" * 65)
    print("  ALL PYSPARK DEMONSTRATIONS COMPLETED SUCCESSFULLY")
    print("=" * 65 + "\n")

    spark.stop()


if __name__ == "__main__":
    main()
