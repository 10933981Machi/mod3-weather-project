"""
io.py

Handles loading weather datasets from CSV files using pandas.
Includes a generator for memory-efficient row-by-row processing.
"""

from pathlib import Path
import csv
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def weather_records_generator(csv_path: str | Path):
    """
    Generator that yields weather records from a CSV file as dictionaries.
    Provides memory-efficient processing without loading entire file into memory.

    Args:
        csv_path: Path to the CSV file.

    Yields:
        Dictionary representing each weather record.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        Exception: If there is an error reading the file.
    """
    csv_path = Path(csv_path)
    
    try:
        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        logger.debug(f"Opening CSV file: {csv_path}")
        with open(csv_path, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                logger.error("CSV file is empty or has no headers")
                raise ValueError("CSV file is empty or has no headers")
            for row in reader:
                yield row
        logger.info(f"Successfully read CSV from {csv_path.name}")
    except FileNotFoundError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        raise


def load_weather_csv(csv_path: str | Path) -> pd.DataFrame:
    """
    Load a weather CSV file into a pandas DataFrame.

    Args:
        csv_path: Path to the CSV file.

    Returns:
        A pandas DataFrame containing the dataset.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        Exception: If there is an error loading the file.
    """
    csv_path = Path(csv_path)
    
    try:
        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        logger.info(f"Loading CSV file: {csv_path}")
        df = pd.read_csv(csv_path)
        logger.info(f"Successfully loaded {len(df)} rows from {csv_path.name}")
        return df
    except FileNotFoundError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        logger.error(f"Error loading CSV file: {e}")
        raise
