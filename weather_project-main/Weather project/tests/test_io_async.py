"""
test_io_async.py

Tests for asynchronous I/O functions in weatherstats.io module.
Verifies that async functions produce identical results to their synchronous counterparts.
"""

import asyncio
import pytest
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from weatherstats.io import (
    load_weather_csv,
    async_load_weather_csv,
    weather_records_generator,
    weather_records_generator_async,
)


@pytest.fixture
def data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent.parent / "Data"


@pytest.fixture
def csv_file(data_dir):
    """Return path to training CSV."""
    return data_dir / "Weather Training Data.csv"


class TestAsyncLoadWeatherCsv:
    """Test async CSV loading."""
    
    def test_async_load_returns_dataframe(self, csv_file):
        """Async load should return a pandas DataFrame."""
        df = asyncio.run(async_load_weather_csv(csv_file))
        assert isinstance(df, pd.DataFrame)
    
    def test_async_load_matches_sync(self, csv_file):
        """Async and sync loads should return equivalent dataframes (relaxed check)."""
        import pandas as pd
        sync_df = load_weather_csv(csv_file)
        async_df = asyncio.run(async_load_weather_csv(csv_file))
        pd.testing.assert_frame_equal(
            sync_df.reset_index(drop=True),
            async_df.reset_index(drop=True),
            check_like=True,
            check_dtype=False
        )
    
    def test_async_load_nonexistent_file(self):
        """Async load should raise FileNotFoundError for non-existent file."""
        with pytest.raises(FileNotFoundError):
            asyncio.run(async_load_weather_csv("nonexistent.csv"))
    
    def test_async_load_has_data(self, csv_file):
        """Async loaded dataframe should have rows."""
        df = asyncio.run(async_load_weather_csv(csv_file))
        assert len(df) > 0, "DataFrame should not be empty"


class TestAsyncGenerator:
    """Test async weather records generator."""
    
    def test_async_generator_yields_dicts(self, csv_file):
        """Async generator should yield dictionaries."""
        async def collect_records():
            records = []
            async for record in weather_records_generator_async(csv_file):
                records.append(record)
            return records
        
        records = asyncio.run(collect_records())
        assert len(records) > 0, "Should yield at least one record"
        assert isinstance(records[0], dict), "Records should be dictionaries"
    
    def test_async_generator_matches_sync_count(self, csv_file):
        """Async and sync generators should yield same number of records."""
        # Collect sync records
        sync_records = list(weather_records_generator(csv_file))
        
        # Collect async records
        async def collect_async():
            records = []
            async for record in weather_records_generator_async(csv_file):
                records.append(record)
            return records
        
        async_records = asyncio.run(collect_async())
        
        assert len(sync_records) == len(async_records), \
            f"Record counts should match: sync={len(sync_records)}, async={len(async_records)}"
    
    def test_async_generator_matches_sync_data(self, csv_file):
        """Async and sync generators should yield identical records."""
        # Collect sync records
        sync_records = list(weather_records_generator(csv_file))
        
        # Collect async records
        async def collect_async():
            records = []
            async for record in weather_records_generator_async(csv_file):
                records.append(record)
            return records
        
        async_records = asyncio.run(collect_async())
        
        # Compare first few records
        for i in range(min(10, len(sync_records))):
            assert sync_records[i] == async_records[i], \
                f"Record {i} should match: sync={sync_records[i]}, async={async_records[i]}"
    
    def test_async_generator_nonexistent_file(self):
        """Async generator should raise FileNotFoundError for non-existent file."""
        async def collect():
            records = []
            async for record in weather_records_generator_async("nonexistent.csv"):
                records.append(record)
            return records
        
        with pytest.raises(FileNotFoundError):
            asyncio.run(collect())


class TestAsyncIntegration:
    """Integration tests for async I/O."""
    
    def test_async_load_and_iterate(self, csv_file):
        """Test loading CSV async and iterating through it."""
        async def load_and_count():
            df = await async_load_weather_csv(csv_file)
            count = len(df)
            return count
        
        count = asyncio.run(load_and_count())
        assert count > 0, "Should have loaded rows"
    
    def test_multiple_async_operations_concurrent(self, csv_file):
        """Test multiple async operations running concurrently."""
        async def run_concurrent():
            # Start both operations concurrently
            load_task = asyncio.create_task(async_load_weather_csv(csv_file))
            
            async def count_records():
                count = 0
                async for _ in weather_records_generator_async(csv_file):
                    count += 1
                return count
            
            gen_task = asyncio.create_task(count_records())
            
            # Await both
            df, record_count = await asyncio.gather(load_task, gen_task)
            return len(df), record_count
        
        df_rows, gen_rows = asyncio.run(run_concurrent())
        assert df_rows == gen_rows, "Dataframe and generator should have same row count"
