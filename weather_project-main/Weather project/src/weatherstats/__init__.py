"""
weatherstats package
OOP-based loader + analyzer for the weather dataset.
"""

from .io import load_weather_csv
from .stats import WeatherDataStore, WeatherAnalyzer

__all__ = ["load_weather_csv", "WeatherDataStore", "WeatherAnalyzer"]
