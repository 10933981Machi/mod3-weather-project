"""
stats.py

Provides classes for storing weather data and computing descriptive statistics
using pandas. Refactored from a functional approach to an OOP-based design.
"""

import pandas as pd


class WeatherDataStore:
    """
    Stores a weather dataset and provides controlled access to it.
    Demonstrates encapsulation.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df

    def get_dataframe(self) -> pd.DataFrame:
        """Return the stored DataFrame."""
        return self._df

    def __len__(self) -> int:
        """Return number of rows in the dataset."""
        return len(self._df)


class WeatherAnalyzer:
    """
    Performs data processing and analysis on a WeatherDataStore.
    Demonstrates composition.
    """

    def __init__(self, store: WeatherDataStore) -> None:
        self._store = store

    def descriptive_stats(self, column: str) -> dict:
        """
        Compute descriptive statistics for a numeric column.

        Stats included:
        - count
        - mean
        - median
        - mode
        - min
        - max
        - range
        - standard deviation
        - variance
        """
        df = self._store.get_dataframe()

        if column not in df.columns:
            return {"column": column, "error": "Column not found"}

        series = pd.to_numeric(df[column], errors="coerce").dropna()
        if series.empty:
            return {"column": column, "error": "No valid numeric values found"}

        mode_vals = series.mode()
        mode = mode_vals.iloc[0] if not mode_vals.empty else None

        return {
            "column": column,
            "count": int(series.count()),
            "mean": float(series.mean()),
            "median": float(series.median()),
            "mode": float(mode) if mode is not None else None,
            "min": float(series.min()),
            "max": float(series.max()),
            "range": float(series.max() - series.min()),
            "std": float(series.std()),
            "var": float(series.var()),
        }
