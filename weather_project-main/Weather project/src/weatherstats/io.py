"""
io.py

Handles loading weather datasets from CSV files using pandas.
"""

from pathlib import Path
import pandas as pd


def load_weather_csv(csv_path: str | Path) -> pd.DataFrame:
    """
    Load a weather CSV file into a pandas DataFrame.

    Args:
        csv_path: Path to the CSV file.

    Returns:
        A pandas DataFrame containing the dataset.
    """
    csv_path = Path(csv_path)
    return pd.read_csv(csv_path)
