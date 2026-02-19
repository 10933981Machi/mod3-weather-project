"""
Simple tests for visualization functions.
they run plotting functions and assert outputs exist.
"""

import pytest
from pathlib import Path
import pandas as pd
import sys

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

from weatherstats import load_weather_csv
from weatherstats.viz import create_all_plots

def test_create_all_plots_saves_files(tmp_path):
    csv_path = project_root / "Data" / "Weather Test Data.csv"
    df = load_weather_csv(csv_path)
    out = tmp_path / "viz_out"
    results = create_all_plots(df, out)
    # check that at least one image was produced and total_rainfall computed
    assert "total_rainfall" in results
    assert results["total_rainfall"] >= 0
    # ensure at least one of the expected image entries is not None
    assert any(results.get(k) for k in ["time_series_max_temp", "rainfall_histogram", "box_temps_by_month", "top_locations_by_rain"]) 
