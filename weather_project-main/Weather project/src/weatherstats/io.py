"""
io.py

Handles loading weather datasets from CSV files using pandas.
Includes a generator for memory-efficient row-by-row processing.
Provides both synchronous and asynchronous APIs.
"""

from pathlib import Path
import csv
import pandas as pd
import logging
import asyncio

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


async def async_load_weather_csv(csv_path: str | Path) -> pd.DataFrame:
    """
    Asynchronously load a weather CSV file into a pandas DataFrame.
    
    Runs the synchronous load_weather_csv in a thread pool via asyncio.to_thread,
    preventing the event loop from being blocked by I/O operations.
    
    Args:
        csv_path: Path to the CSV file.
    
    Returns:
        A pandas DataFrame containing the dataset.
    
    Raises:
        FileNotFoundError: If the CSV file does not exist.
        Exception: If there is an error loading the file.
    """
    csv_path = Path(csv_path)
    logger.debug(f"Starting async load of CSV: {csv_path}")
    try:
        df = await asyncio.to_thread(load_weather_csv, csv_path)
        logger.info(f"Async load completed for {csv_path.name}")
        return df
    except Exception as e:
        logger.error(f"Error in async_load_weather_csv: {e}")
        raise


async def weather_records_generator_async(csv_path: str | Path):
    """
    Asynchronously yield weather records from a CSV file.
    
    Wraps the synchronous weather_records_generator via asyncio.to_thread,
    allowing non-blocking iteration through records without blocking the event loop.
    
    Args:
        csv_path: Path to the CSV file.
    
    Yields:
        Dictionary representing each weather record.
    
    Raises:
        FileNotFoundError: If the CSV file does not exist.
        Exception: If there is an error reading the file.
    """
    csv_path = Path(csv_path)
    logger.debug(f"Starting async generator for: {csv_path}")
    def get_records():
        return list(weather_records_generator(csv_path))
    try:
        records = await asyncio.to_thread(get_records)
        for record in records:
            yield record
    except Exception as e:
        logger.error(f"Error in weather_records_generator_async: {e}")
        raise
