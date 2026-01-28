"""
weatherstats package

This package provides tools for loading weather CSV datasets using pandas
and calculating descriptive statistics.
"""

from .io import load_weather_csv
from .stats import descriptive_stats

__all__ = ["load_weather_csv", "descriptive_stats"]
