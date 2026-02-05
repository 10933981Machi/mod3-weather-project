import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from weatherstats import load_weather_csv, weather_records_generator, WeatherDataStore, WeatherAnalyzer

# Configure logging to show it in action
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)


def main() -> None:
    try:
        # Find project root
        project_root = Path(__file__).resolve().parents[1]
        csv_path = project_root / "Data" / "Weather Training Data.csv"

        print("\n" + "="*60)
        print("WEATHER STATS - Module 4 (Generators & Iterators)")
        print("="*60)

        # 1. Demonstrate Generator - weather_records_generator
        print("\n[GENERATOR] Reading first 3 records using generator:")
        print("-" * 60)
        gen = weather_records_generator(csv_path)
        for i, record in enumerate(gen):
            if i < 3:
                print(f"  Record {i+1}: Location={record['Location']}, MaxTemp={record['MaxTemp']}")
            else:
                break

        # 2. Load data with error handling
        print("\n[DATA LOADING] Loading data with error handling:")
        print("-" * 60)
        df = load_weather_csv(csv_path)
        print(f"✓ Loaded {len(df)} rows, {len(df.columns)} columns")

        # 3. Create store and analyzer
        store = WeatherDataStore(df)
        analyzer = WeatherAnalyzer(store)

        # 4. Demonstrate Iterator - WeatherDataStore is now iterable
        print("\n[ITERATOR] Using WeatherDataStore iterator (first 3 rows):")
        print("-" * 60)
        for i, record in enumerate(store):
            if i < 3:
                print(f"  Row {i+1}: {record.get('Location')} - MinTemp: {record.get('MinTemp')}")
            else:
                break

        # 5. Compute statistics with error handling
        print("\n[STATISTICS] Computing descriptive stats with error handling:")
        print("-" * 60)
        columns_to_check = ["MinTemp", "MaxTemp", "Rainfall"]

        for col in columns_to_check:
            stats = analyzer.descriptive_stats(col)
            if "error" in stats:
                print(f"✗ {col}: {stats['error']}")
            else:
                print(f"✓ {col}: Mean={stats['mean']:.2f}, Median={stats['median']:.2f}, Range={stats['range']:.2f}")

        print("\n" + "="*60)
        print("✓ ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")

    except FileNotFoundError as e:
        print(f"\n✗ File Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
