"""
viz.py

Plotting helpers for weather analysis using matplotlib and seaborn.
Includes examples using map, filter, reduce, and lambda expressions
to demonstrate functional-style data filtering/aggregation.
Includes parallel plotting for multi-core utilization of plot rendering.
"""

from pathlib import Path
from functools import reduce
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import os
from concurrent.futures import ProcessPoolExecutor

sns.set(style="whitegrid")


def ensure_output_dir(output_dir: Path | str):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    return out


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # parse Date if present
    if "Date" in df.columns:
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce", infer_datetime_format=True)
        # helpful derived columns
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month
    return df


def filter_rainy_days(df: pd.DataFrame) -> pd.DataFrame:
    # Use filter + lambda over row dicts to select rows where Rainfall > 0
    records = df.to_dict(orient="records")
    rainy = list(filter(lambda r: (r.get("Rainfall") not in (None, "")) and float(r.get("Rainfall") or 0) > 0, records))
    return pd.DataFrame(rainy)


def total_rainfall_reduce(df: pd.DataFrame) -> float:
    # Use map to extract rainfall numbers and reduce to sum
    records = df.to_dict(orient="records")
    rainfall_vals = map(lambda r: float(r.get("Rainfall") or 0), records)
    total = reduce(lambda a, b: a + b, rainfall_vals, 0.0)
    return total


def high_temperature_days(df: pd.DataFrame, threshold: float = 35.0) -> pd.DataFrame:
    # Use map to convert MaxTemp to numeric and filter via list comprehension
    recs = df.to_dict(orient="records")
    hot = list(filter(lambda r: (r.get("MaxTemp") not in (None, "")) and float(r.get("MaxTemp") or -999) >= threshold, recs))
    return pd.DataFrame(hot)


def plot_time_series_max_temp(df: pd.DataFrame, output_dir: Path | str):
    out = ensure_output_dir(output_dir)
    df = prepare_dataframe(df)
    if "Date" not in df.columns or df["Date"].isna().all():
        raise ValueError("Date column missing or couldn't be parsed for time series plot.")
    # group by date (daily average)
    series = df.groupby("Date").agg({"MaxTemp": lambda s: pd.to_numeric(s, errors="coerce").mean()})
    plt.figure(figsize=(12, 4))
    plt.plot(series.index, series["MaxTemp"], color="tab:red")
    plt.title("Daily Average Max Temperature")
    plt.xlabel("Date")
    plt.ylabel("MaxTemp (°C)")
    plt.tight_layout()
    out_path = out / "time_series_max_temp.png"
    plt.savefig(out_path)
    plt.close()
    return out_path


def plot_rainfall_histogram(df: pd.DataFrame, output_dir: Path | str):
    out = ensure_output_dir(output_dir)
    df = prepare_dataframe(df)
    rainfall = pd.to_numeric(df.get("Rainfall", pd.Series()), errors="coerce").dropna()
    plt.figure(figsize=(8, 4))
    sns.histplot(rainfall, bins=40, kde=True, color="tab:blue")
    plt.title("Rainfall Distribution")
    plt.xlabel("Rainfall (mm)")
    plt.tight_layout()
    out_path = out / "rainfall_histogram.png"
    plt.savefig(out_path)
    plt.close()
    return out_path


def plot_max_temp_histogram(df: pd.DataFrame, output_dir: Path | str):
    out = ensure_output_dir(output_dir)
    max_temp = pd.to_numeric(df.get("MaxTemp", pd.Series()), errors="coerce").dropna()
    plt.figure(figsize=(8, 4))
    sns.histplot(max_temp, bins=40, kde=True, color="tab:orange")
    plt.title("Max Temperature Distribution")
    plt.xlabel("MaxTemp (°C)")
    plt.tight_layout()
    out_path = out / "max_temp_histogram.png"
    plt.savefig(out_path)
    plt.close()
    return out_path


def plot_temp_vs_rain_scatter(df: pd.DataFrame, output_dir: Path | str):
    out = ensure_output_dir(output_dir)
    x = pd.to_numeric(df.get("Rainfall", pd.Series()), errors="coerce")
    y = pd.to_numeric(df.get("MaxTemp", pd.Series()), errors="coerce")
    mask = x.notna() & y.notna()
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=x[mask], y=y[mask], alpha=0.4)
    plt.xlabel("Rainfall (mm)")
    plt.ylabel("MaxTemp (°C)")
    plt.title("MaxTemp vs Rainfall")
    plt.tight_layout()
    out_path = out / "temp_vs_rain_scatter.png"
    plt.savefig(out_path)
    plt.close()
    return out_path


def plot_box_temps_by_location(df: pd.DataFrame, output_dir: Path | str, top_n: int = 10):
    out = ensure_output_dir(output_dir)
    if "Location" not in df.columns:
        raise ValueError("Location column not found for location-based boxplot.")
    df_local = df.copy()
    df_local["MaxTemp"] = pd.to_numeric(df_local.get("MaxTemp"), errors="coerce")
    df_local["MinTemp"] = pd.to_numeric(df_local.get("MinTemp"), errors="coerce")
    agg = df_local.groupby("Location")["MaxTemp"].median().sort_values(ascending=False).head(top_n)
    top_locations = agg.index.tolist()
    sub = df_local[df_local["Location"].isin(top_locations)]
    melt = sub.melt(id_vars=["Location"], value_vars=["MinTemp", "MaxTemp"], var_name="TempType", value_name="Temp")
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="TempType", y="Temp", hue="Location", data=melt)
    plt.title(f"Temperature Distribution for Top {top_n} Locations (by median MaxTemp)")
    plt.tight_layout()
    out_path = out / "box_temps_by_location.png"
    plt.savefig(out_path)
    plt.close()
    return out_path


def plot_box_temps_by_month(df: pd.DataFrame, output_dir: Path | str):
    out = ensure_output_dir(output_dir)
    df = prepare_dataframe(df)
    # prepare numeric columns
    df["MinTemp"] = pd.to_numeric(df.get("MinTemp"), errors="coerce")
    df["MaxTemp"] = pd.to_numeric(df.get("MaxTemp"), errors="coerce")
    melt = df.melt(id_vars=["Month"], value_vars=["MinTemp", "MaxTemp"], var_name="TempType", value_name="Temp")
    plt.figure(figsize=(10, 5))
    sns.boxplot(x="Month", y="Temp", hue="TempType", data=melt)
    plt.title("Temperature Distribution by Month")
    plt.tight_layout()
    out_path = out / "box_temps_by_month.png"
    plt.savefig(out_path)
    plt.close()
    return out_path


def plot_top_locations_by_rain(df: pd.DataFrame, output_dir: Path | str, top_n: int = 10):
    out = ensure_output_dir(output_dir)
    df = prepare_dataframe(df)
    if "Location" not in df.columns:
        raise ValueError("Location column not found for location-based plot.")
    df["Rainfall"] = pd.to_numeric(df.get("Rainfall"), errors="coerce").fillna(0)
    agg = df.groupby("Location")["Rainfall"].mean().sort_values(ascending=False).head(top_n)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=agg.values, y=agg.index, palette="Blues_d")
    plt.xlabel("Average Rainfall (mm)")
    plt.title(f"Top {top_n} Locations by Average Rainfall")
    plt.tight_layout()
    out_path = out / "top_locations_by_rain.png"
    plt.savefig(out_path)
    plt.close()
    return out_path


def create_all_plots(df: pd.DataFrame, output_dir: Path | str):
    out = ensure_output_dir(output_dir)
    outputs = {}
    # create plots; each function returns path to saved image
    # If Date is present and parseable, create time-series and month-based boxplots.
    if "Date" in df.columns:
        try:
            outputs["time_series_max_temp"] = plot_time_series_max_temp(df, out)
        except Exception:
            outputs["time_series_max_temp"] = None
        try:
            outputs["box_temps_by_month"] = plot_box_temps_by_month(df, out)
        except Exception:
            outputs["box_temps_by_month"] = None
    else:
        # Fallback visualizations when no Date column exists
        try:
            outputs["max_temp_histogram"] = plot_max_temp_histogram(df, out)
        except Exception:
            outputs["max_temp_histogram"] = None
        try:
            outputs["temp_vs_rain_scatter"] = plot_temp_vs_rain_scatter(df, out)
        except Exception:
            outputs["temp_vs_rain_scatter"] = None
        try:
            outputs["box_temps_by_location"] = plot_box_temps_by_location(df, out)
        except Exception:
            outputs["box_temps_by_location"] = None

    try:
        outputs["rainfall_histogram"] = plot_rainfall_histogram(df, out)
    except Exception:
        outputs["rainfall_histogram"] = None
    try:
        outputs["top_locations_by_rain"] = plot_top_locations_by_rain(df, out)
    except Exception:
        outputs["top_locations_by_rain"] = None

    # Demonstrate functional reduce example
    outputs["total_rainfall"] = total_rainfall_reduce(df)
    return outputs


def create_all_plots_parallel(csv_path: Path | str, output_dir: Path | str, workers: int | None = None) -> dict:
    """
    Create all plots in parallel using ProcessPoolExecutor.
    
    Distributes plot generation across multiple worker processes for improved performance
    on multi-core systems. Each worker loads the CSV independently and generates independent plots.
    
    Args:
        csv_path: Path to the CSV data file.
        output_dir: Directory to save output plots.
        workers: Number of worker processes. If None, defaults to os.cpu_count().
    
    Returns:
        Dictionary mapping plot names to output paths and metrics (same as create_all_plots).
    """
    csv_path = Path(csv_path)
    out = ensure_output_dir(output_dir)
    
    if workers is None:
        workers = os.cpu_count() or 1
    
    # Define plot jobs: (function_name, worker_function, args)
    plot_jobs = [
        ("rainfall_histogram", _plot_rainfall_histogram_worker, (csv_path, out)),
        ("max_temp_histogram", _plot_max_temp_histogram_worker, (csv_path, out)),
        ("temp_vs_rain_scatter", _plot_temp_vs_rain_scatter_worker, (csv_path, out)),
        ("box_temps_by_location", _plot_box_temps_by_location_worker, (csv_path, out)),
        ("top_locations_by_rain", _plot_top_locations_by_rain_worker, (csv_path, out)),
    ]
    
    outputs = {}
    
    try:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            # Submit all jobs in parallel
            futures = {executor.submit(job[1], *job[2]): job[0] for job in plot_jobs}
            
            # Collect results as they complete
            for future in futures:
                plot_name = futures[future]
                try:
                    result = future.result()
                    outputs[plot_name] = result
                except Exception as e:
                    outputs[plot_name] = None
    except Exception as e:
        # Fallback to serial execution
        for plot_name, worker_func, args in plot_jobs:
            try:
                result = worker_func(*args)
                outputs[plot_name] = result
            except Exception:
                outputs[plot_name] = None
    
    # Add total rainfall (computed here, not expensive enough for parallel)
    try:
        df = pd.read_csv(csv_path)
        # Ensure Rainfall is numeric and NaN handled
        df["Rainfall"] = pd.to_numeric(df.get("Rainfall", pd.Series()), errors="coerce").fillna(0)
        outputs["total_rainfall"] = total_rainfall_reduce(df)
    except Exception:
        outputs["total_rainfall"] = None
    
    return outputs


def _plot_rainfall_histogram_worker(csv_path: Path | str, output_dir: Path) -> Path | None:
    """Worker function: plot rainfall histogram. Runs in separate process."""
    try:
        matplotlib.use('Agg')  # Use non-interactive backend
        df = pd.read_csv(csv_path)
        rainfall = pd.to_numeric(df.get("Rainfall", pd.Series()), errors="coerce").dropna()
        plt.figure(figsize=(8, 4))
        sns.histplot(rainfall, bins=40, kde=True, color="tab:blue")
        plt.title("Rainfall Distribution")
        plt.xlabel("Rainfall (mm)")
        plt.tight_layout()
        out_path = output_dir / "rainfall_histogram.png"
        plt.savefig(out_path)
        plt.close()
        return out_path
    except Exception:
        return None


def _plot_max_temp_histogram_worker(csv_path: Path | str, output_dir: Path) -> Path | None:
    """Worker function: plot max temp histogram. Runs in separate process."""
    try:
        matplotlib.use('Agg')
        df = pd.read_csv(csv_path)
        max_temp = pd.to_numeric(df.get("MaxTemp", pd.Series()), errors="coerce").dropna()
        plt.figure(figsize=(8, 4))
        sns.histplot(max_temp, bins=40, kde=True, color="tab:orange")
        plt.title("Max Temperature Distribution")
        plt.xlabel("MaxTemp (°C)")
        plt.tight_layout()
        out_path = output_dir / "max_temp_histogram.png"
        plt.savefig(out_path)
        plt.close()
        return out_path
    except Exception:
        return None


def _plot_temp_vs_rain_scatter_worker(csv_path: Path | str, output_dir: Path) -> Path | None:
    """Worker function: plot temperature vs rainfall scatter. Runs in separate process."""
    try:
        matplotlib.use('Agg')
        df = pd.read_csv(csv_path)
        x = pd.to_numeric(df.get("Rainfall", pd.Series()), errors="coerce")
        y = pd.to_numeric(df.get("MaxTemp", pd.Series()), errors="coerce")
        mask = x.notna() & y.notna()
        plt.figure(figsize=(8, 6))
        sns.scatterplot(x=x[mask], y=y[mask], alpha=0.4)
        plt.xlabel("Rainfall (mm)")
        plt.ylabel("MaxTemp (°C)")
        plt.title("MaxTemp vs Rainfall")
        plt.tight_layout()
        out_path = output_dir / "temp_vs_rain_scatter.png"
        plt.savefig(out_path)
        plt.close()
        return out_path
    except Exception:
        return None


def _plot_box_temps_by_location_worker(csv_path: Path | str, output_dir: Path, top_n: int = 10) -> Path | None:
    """Worker function: plot box temps by location. Runs in separate process."""
    try:
        matplotlib.use('Agg')
        df = pd.read_csv(csv_path)
        if "Location" not in df.columns:
            return None
        df["MaxTemp"] = pd.to_numeric(df.get("MaxTemp"), errors="coerce")
        df["MinTemp"] = pd.to_numeric(df.get("MinTemp"), errors="coerce")
        agg = df.groupby("Location")["MaxTemp"].median().sort_values(ascending=False).head(top_n)
        top_locations = agg.index.tolist()
        sub = df[df["Location"].isin(top_locations)]
        melt = sub.melt(id_vars=["Location"], value_vars=["MinTemp", "MaxTemp"], var_name="TempType", value_name="Temp")
        plt.figure(figsize=(10, 6))
        sns.boxplot(x="TempType", y="Temp", hue="Location", data=melt)
        plt.title(f"Temperature Distribution for Top {top_n} Locations (by median MaxTemp)")
        plt.tight_layout()
        out_path = output_dir / "box_temps_by_location.png"
        plt.savefig(out_path)
        plt.close()
        return out_path
    except Exception:
        return None


def _plot_top_locations_by_rain_worker(csv_path: Path | str, output_dir: Path, top_n: int = 10) -> Path | None:
    """Worker function: plot top locations by rainfall. Runs in separate process."""
    try:
        matplotlib.use('Agg')
        df = pd.read_csv(csv_path)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce", infer_datetime_format=True)
        if "Location" not in df.columns:
            return None
        df["Rainfall"] = pd.to_numeric(df.get("Rainfall"), errors="coerce").fillna(0)
        agg = df.groupby("Location")["Rainfall"].mean().sort_values(ascending=False).head(top_n)
        plt.figure(figsize=(10, 6))
        sns.barplot(x=agg.values, y=agg.index, palette="Blues_d")
        plt.xlabel("Average Rainfall (mm)")
        plt.title(f"Top {top_n} Locations by Average Rainfall")
        plt.tight_layout()
        out_path = output_dir / "top_locations_by_rain.png"
        plt.savefig(out_path)
        plt.close()
        return out_path
    except Exception:
        return None
