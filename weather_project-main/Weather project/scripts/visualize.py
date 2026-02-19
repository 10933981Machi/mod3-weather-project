#!/usr/bin/env python3
"""
Simple CLI to generate and save visualizations.
Run from project folder: python3 scripts/visualize.py
"""

import sys
from pathlib import Path
import logging
import pandas as pd

# add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from weatherstats.io import load_weather_csv
from weatherstats.viz import create_all_plots

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main():
    project_root = Path(__file__).resolve().parents[1]
    csv_path = project_root / "Data" / "Weather Training Data.csv"
    logging.info(f"Loading CSV from {csv_path}")
    df = load_weather_csv(csv_path)
    out = project_root / "visualizations"
    logging.info(f"Creating visualizations in {out}")
    results = create_all_plots(df, out)
    logging.info("Visualization results:")
    for k, v in results.items():
        logging.info(f" - {k}: {v}")
    logging.info("✓ All visualizations attempted. Inspect saved images in visualizations/")


if __name__ == "__main__":
    main()
