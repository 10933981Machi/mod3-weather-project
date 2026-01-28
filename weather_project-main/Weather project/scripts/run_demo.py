from pathlib import Path
from weatherstats.io import load_weather_csv
from weatherstats.stats import WeatherDataStore, WeatherAnalyzer


def main() -> None:
    # Find project root based on this script location
    project_root = Path(__file__).resolve().parents[1]
    csv_path = project_root / "Data" / "Weather Training Data.csv"

    # Load data
    df = load_weather_csv(csv_path)

    # Store data (encapsulation)
    store = WeatherDataStore(df)

    # Analyzer uses the store (composition)
    analyzer = WeatherAnalyzer(store)

    print(f"Loaded {len(store)} rows.")
    print("Columns:", list(store.get_dataframe().columns))

    # Stats for a few numeric columns
    columns_to_check = ["MinTemp", "MaxTemp", "Rainfall", "WindGustSpeed", "Humidity9am"]

    for col in columns_to_check:
        stats = analyzer.descriptive_stats(col)
        print("\nStats:", stats)


if __name__ == "__main__":
    main()
