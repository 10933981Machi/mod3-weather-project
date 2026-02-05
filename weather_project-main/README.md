# weather_project (Module 4 – Generators, Iterators & Error Handling)

## Dataset
I used the **Australian Weather Data** dataset from Kaggle (CSV format).  
The training file loads **99,516 rows**.

Files:
- `Data/Weather Training Data.csv`
- `Data/Weather Test Data.csv`

## Module 4 Refactoring - What Changed

### 1. **Generator** - `weather_records_generator()`
**Location:** `src/weatherstats/io.py`

- **Purpose:** Yields weather records from CSV file one at a time instead of loading entire file into memory
- **Implementation:** Uses Python's `csv.DictReader` to lazily read rows
- **Benefit:** Memory-efficient for large datasets; can process millions of records without loading all into RAM
- **Usage in demo:** First demonstration shows reading first 3 records using the generator

### 2. **Iterator** - `WeatherDataStore.__iter__()`
**Location:** `src/weatherstats/stats.py`

- **Purpose:** Makes `WeatherDataStore` iterable by implementing `__iter__()` method
- **Implementation:** Iterates through DataFrame rows and yields them as dictionaries
- **Benefit:** Allows natural Python iteration syntax: `for record in store:`
- **Usage in demo:** Second demonstration shows iterating through first 3 rows stored in WeatherDataStore

### 3. **Error Handling**
**Locations:** `src/weatherstats/io.py` and `src/weatherstats/stats.py`

#### In `io.py`:
- File existence validation before processing
- Try-except blocks for file I/O operations
- Proper error messages logged for debugging

#### In `stats.py`:
- Column existence checks before computation
- Try-except wrapper in `descriptive_stats()` method
- Graceful handling of invalid or missing data
- Warning logs when data is unavailable

### 4. **Logging System**
**Location:** All modules (`src/weatherstats/__init__.py`, `io.py`, `stats.py`)

- **Configuration:** Logger setup in package `__init__.py`
- **Usage:** All modules use `logger = logging.getLogger(__name__)` to get module-specific logger
- **Levels:** INFO for major operations, DEBUG for iterator creation, WARNING for data issues, ERROR for failures
- **Benefit:** Transparent view of what the application is doing without changing any outputs

## Code Changes Summary

| Component | Change | Reason |
|-----------|--------|--------|
| `weather_records_generator()` | New generator function | Memory-efficient CSV reading |
| `WeatherDataStore.__iter__()` | New iterator method | Makes class iterable |
| Error handling | Added try-except blocks | Robust file and data validation |
| Logging | Added logger configuration | Transparent debugging and monitoring |

## Running the Demo

From inside the `Weather project/` folder:

```bash
python3 scripts/run_demo.py
```

The demo demonstrates:
1. **Generator:** Reads CSV records lazily without loading entire file
2. **Iterator:** Traverses stored data using Python iteration protocol
3. **Error Handling:** Gracefully handles file and data validation errors
4. **Logging:** Shows INFO, WARNING, and ERROR messages for operations

Expected output shows successful generator and iterator usage with 99,516 rows loaded and statistics computed for temperature and rainfall columns.

## Design Principles Maintained

- ✓ No new source files created
- ✓ All existing class and function names preserved  
- ✓ Logic and outputs unchanged
- ✓ Minimal, readable refactoring
- ✓ Backward compatible with existing code
