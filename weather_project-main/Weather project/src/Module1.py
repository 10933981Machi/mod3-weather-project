import csv
from pathlib import Path

weather_data = []


def load_csv(file_name: str) -> None:
    """
    Load weather data from a CSV file into the global `weather_data` list.

    This function opens the CSV file, creates a CSV reader, and passes it to
    `add_to_weather_data()` to convert each row into a dictionary.

    Args:
        file_name (str): The path to the CSV file to read.

    Returns:
        None
    """
    with open(file_name, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        add_to_weather_data(reader)


def add_to_weather_data(reader: csv.reader) -> None:
    """
    Convert CSV rows into dictionaries and store them in the global `weather_data` list.

    The first row of the CSV is treated as the header row (column names).
    Each remaining row is converted into a dictionary where:
        - keys = header names
        - values = row values (stored as strings)

    Args:
        reader (csv.reader): A CSV reader object containing the file's rows.

    Returns:
        None
    """
    global weather_data

    headers = next(reader)
    for row in reader:
        weather_data.append(dict(zip(headers, row)))


if __name__ == "__main__":
    # Get the folder your script is inside (src/)
    script_dir = Path(__file__).parent

    # Build the correct path to the CSV in Data/
    csv_path = script_dir.parent / "Data" / "Weather Training Data.csv"

    load_csv(csv_path)
    print(f"Loaded {len(weather_data)} rows.")
    print("First row:", weather_data[0])