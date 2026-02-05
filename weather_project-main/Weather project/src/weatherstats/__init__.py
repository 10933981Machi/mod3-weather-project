"""
weatherstats package
OOP-based loader + analyzer for the weather dataset.
"""

import logging

from .io import load_weather_csv, weather_records_generator
from .stats import WeatherDataStore, WeatherAnalyzer

__all__ = ["load_weather_csv", "weather_records_generator", "WeatherDataStore", "WeatherAnalyzer"]

# Configure logging for the package
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
