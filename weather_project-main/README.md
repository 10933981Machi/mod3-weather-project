# weather_project (Module 3 – OOP Refactor)

## Dataset
I used the **Australian Weather Data** dataset from Kaggle (CSV format).  
The training file loads **99,516 rows**.

Files:
- `Data/Weather Training Data.csv`
- `Data/Weather Test Data.csv`

## OOP Design (What Changed)
For this phase, I refactored the code to use classes:

- **WeatherDataStore**
  - Stores the pandas DataFrame
  - Controls access to the dataset
  - Demonstrates encapsulation

- **WeatherAnalyzer**
  - Uses a WeatherDataStore object
  - Computes descriptive statistics (mean, median, mode, range, etc.)
  - Demonstrates composition

This keeps data storage and data processing separate and makes the code easier to extend later.

## Run Demo
From inside the `Weather project/` folder:

```bash
python3 scripts/run_demo.py