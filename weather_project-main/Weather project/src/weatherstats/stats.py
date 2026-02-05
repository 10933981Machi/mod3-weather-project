"""
stats.py

Provides classes for storing weather data and computing descriptive statistics
using pandas. Refactored from a functional approach to an OOP-based design.
Includes an iterator for row-by-row access to the dataset.
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)


class WeatherDataStore:
    """
    Stores a weather dataset and provides controlled access to it.
    Demonstrates encapsulation.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df
        logger.info(f"WeatherDataStore initialized with {len(df)} rows")

    def get_dataframe(self) -> pd.DataFrame:
        """Return the stored DataFrame."""
        return self._df

    def __len__(self) -> int:
        """Return number of rows in the dataset."""
        return len(self._df)
    
    def __iter__(self):
        """
        Make WeatherDataStore iterable. Yields each row as a dictionary.
        Provides an iterator interface for traversing records row-by-row.
        """
        logger.debug(f"Creating iterator for {len(self._df)} rows")
        for _, row in self._df.iterrows():
            yield row.to_dict()


class WeatherAnalyzer:
    """
    Performs data processing and analysis on a WeatherDataStore.
    Demonstrates composition.
    """

    def __init__(self, store: WeatherDataStore) -> None:
        self._store = store
        logger.info("WeatherAnalyzer initialized")

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

        try:
            if column not in df.columns:
                logger.warning(f"Column '{column}' not found in dataset")
                return {"column": column, "error": "Column not found"}

            series = pd.to_numeric(df[column], errors="coerce").dropna()
            if series.empty:
                logger.warning(f"No valid numeric values found in column '{column}'")
                return {"column": column, "error": "No valid numeric values found"}

            mode_vals = series.mode()
            mode = mode_vals.iloc[0] if not mode_vals.empty else None

            logger.debug(f"Computed statistics for column '{column}'")
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
        except Exception as e:
            logger.error(f"Error computing statistics for column '{column}': {e}")
            return {"column": column, "error": str(e)}
