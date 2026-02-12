"""
conftest.py

Pytest configuration file with shared fixtures for the test suite.
Fixtures provide setup data and objects for unit tests.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd

# Add src to path so we can import weatherstats
project_root = Path(__file__).resolve().parents[1]
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from weatherstats import load_weather_csv, WeatherDataStore, WeatherAnalyzer


@pytest.fixture
def csv_training_path():
    """Fixture providing path to training CSV file."""
    return project_root / "Data" / "Weather Training Data.csv"


@pytest.fixture
def csv_test_path():
    """Fixture providing path to test CSV file."""
    return project_root / "Data" / "Weather Test Data.csv"


@pytest.fixture
def training_dataframe(csv_training_path):
    """Fixture providing loaded training data as DataFrame."""
    return load_weather_csv(csv_training_path)


@pytest.fixture
def test_dataframe(csv_test_path):
    """Fixture providing loaded test data as DataFrame."""
    return load_weather_csv(csv_test_path)


@pytest.fixture
def weather_store(training_dataframe):
    """Fixture providing WeatherDataStore with training data."""
    return WeatherDataStore(training_dataframe)


@pytest.fixture
def weather_analyzer(weather_store):
    """Fixture providing WeatherAnalyzer with store."""
    return WeatherAnalyzer(weather_store)
