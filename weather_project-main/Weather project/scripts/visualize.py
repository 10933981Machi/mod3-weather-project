#!/usr/bin/env python3
"""
Simple CLI to generate and save visualizations.
Run from project folder: python3 scripts/visualize.py [--parallel] [--workers N]

Options:
  --parallel    Use parallel processing for plot generation
  --workers N   Number of worker processes (default: cpu count)
"""

import sys
from pathlib import Path
import logging
import pandas as pd
import argparse

# add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from weatherstats.io import load_weather_csv
from weatherstats.viz import create_all_plots, create_all_plots_parallel

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main():
    parser = argparse.ArgumentParser(
        description="Generate weather visualizations from CSV data"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Use parallel processing for plot generation"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of worker processes (default: CPU count)"
    )
    
    args = parser.parse_args()
    
    project_root = Path(__file__).resolve().parents[1]
    csv_path = project_root / "Data" / "Weather Training Data.csv"
    logging.info(f"Loading CSV from {csv_path}")
    df = load_weather_csv(csv_path)
    out = project_root / "visualizations"
    
    if args.parallel:
        logging.info(f"Creating visualizations in {out} (PARALLEL mode, workers={args.workers})")
        results = create_all_plots_parallel(csv_path, out, workers=args.workers)
    else:
        logging.info(f"Creating visualizations in {out} (serial mode)")
        results = create_all_plots(df, out)
    
    logging.info("Visualization results:")
    for k, v in results.items():
        logging.info(f" - {k}: {v}")
    logging.info("✓ All visualizations attempted. Inspect saved images in visualizations/")


if __name__ == "__main__":
    main()
