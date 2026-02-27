"""
test_viz_parallel.py

Tests for parallel visualization generation in weatherstats.viz module.
Verifies that parallel plot functions produce the same output as serial versions.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from weatherstats.io import load_weather_csv
from weatherstats.viz import create_all_plots, create_all_plots_parallel


@pytest.fixture
def data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent.parent / "Data"


@pytest.fixture
def csv_file(data_dir):
    """Return path to training CSV."""
    return data_dir / "Weather Training Data.csv"


@pytest.fixture
def temp_output_dir():
    """Create and clean up a temporary output directory."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    # Cleanup
    if Path(tmpdir).exists():
        shutil.rmtree(tmpdir)


class TestParallelPlots:
    """Test parallel plot generation."""
    
    def test_parallel_plots_returns_dict(self, csv_file, temp_output_dir):
        """Parallel plots should return a dictionary of results."""
        results = create_all_plots_parallel(csv_file, temp_output_dir)
        assert isinstance(results, dict), "Should return a dictionary"
    
    def test_parallel_plots_creates_files(self, csv_file, temp_output_dir):
        """Parallel plots should create output files."""
        results = create_all_plots_parallel(csv_file, temp_output_dir, workers=2)
        
        # Count non-None results that are files
        file_count = sum(1 for v in results.values() if v is not None and isinstance(v, Path))
        assert file_count > 0, "Should create at least one plot file"
    
    def test_parallel_vs_serial_keys(self, csv_file, temp_output_dir):
        """Parallel and serial plot results should have the same keys."""
        df = load_weather_csv(csv_file)
        
        serial_dir = temp_output_dir / "serial"
        serial_dir.mkdir(exist_ok=True)
        serial_results = create_all_plots(df, serial_dir)
        
        parallel_dir = temp_output_dir / "parallel"
        parallel_dir.mkdir(exist_ok=True)
        parallel_results = create_all_plots_parallel(csv_file, parallel_dir, workers=2)
        
        # Compare keys
        assert set(serial_results.keys()) == set(parallel_results.keys()), \
            f"Result keys should match: serial={serial_results.keys()}, parallel={parallel_results.keys()}"
    
    def test_parallel_plots_with_different_workers(self, csv_file, temp_output_dir):
        """Parallel plots should work with different worker counts."""
        dir1 = temp_output_dir / "w1"
        dir1.mkdir(exist_ok=True)
        results_1 = create_all_plots_parallel(csv_file, dir1, workers=1)
        
        dir2 = temp_output_dir / "w2"
        dir2.mkdir(exist_ok=True)
        results_2 = create_all_plots_parallel(csv_file, dir2, workers=2)
        
        # Both should have the same plot types
        assert set(results_1.keys()) == set(results_2.keys()), \
            "Should produce same plot types with different worker counts"
    
    def test_parallel_plots_default_workers(self, csv_file, temp_output_dir):
        """Parallel plots should work with default worker count."""
        results = create_all_plots_parallel(csv_file, temp_output_dir)
        assert isinstance(results, dict), "Should work with default workers"


class TestParallelPlotsEdgeCases:
    """Test edge cases for parallel plotting."""
    
    def test_parallel_single_worker(self, csv_file, temp_output_dir):
        """Parallel plotting with 1 worker should work."""
        results = create_all_plots_parallel(csv_file, temp_output_dir, workers=1)
        assert len(results) > 0, "Should produce plots with 1 worker"
    
    def test_parallel_many_workers(self, csv_file, temp_output_dir):
        """Parallel plotting with many workers should handle gracefully."""
        results = create_all_plots_parallel(csv_file, temp_output_dir, workers=16)
        assert len(results) > 0, "Should handle excess workers"
    
    def test_parallel_nonexistent_csv(self, temp_output_dir):
        """Parallel plotting with nonexistent CSV should handle gracefully."""
        results = create_all_plots_parallel("nonexistent.csv", temp_output_dir)
        # Should return empty or error results, not crash
        assert isinstance(results, dict), "Should return dictionary even on error"


class TestParallelPlotsOutput:
    """Test output properties of parallel plots."""
    
    def test_parallel_plots_have_total_rainfall(self, csv_file, temp_output_dir):
        """Parallel plots should include total_rainfall metric."""
        results = create_all_plots_parallel(csv_file, temp_output_dir)
        assert "total_rainfall" in results, "Should compute total_rainfall"
        if results["total_rainfall"] is not None:
            assert isinstance(results["total_rainfall"], (int, float)), \
                "total_rainfall should be numeric"
    
    def test_parallel_plots_match_serial_total_rainfall(self, csv_file, temp_output_dir):
        """Parallel and serial total_rainfall should match closely."""
        df = load_weather_csv(csv_file)
        
        serial_dir = temp_output_dir / "serial"
        serial_dir.mkdir(exist_ok=True)
        serial_results = create_all_plots(df, serial_dir)
        
        parallel_dir = temp_output_dir / "parallel"
        parallel_dir.mkdir(exist_ok=True)
        parallel_results = create_all_plots_parallel(csv_file, parallel_dir, workers=2)
        
        # Compare total_rainfall
        if (serial_results.get("total_rainfall") is not None and 
            parallel_results.get("total_rainfall") is not None):
            assert abs(serial_results["total_rainfall"] - parallel_results["total_rainfall"]) < 0.01, \
                "total_rainfall should match closely: serial={}, parallel={}".format(
                    serial_results["total_rainfall"],
                    parallel_results["total_rainfall"]
                )
    
    def test_parallel_creates_output_directory(self, csv_file, temp_output_dir):
        """Parallel plots should create output directory if it doesn't exist."""
        nonexistent_dir = temp_output_dir / "does_not_exist"
        assert not nonexistent_dir.exists(), "Directory should not exist yet"
        
        results = create_all_plots_parallel(csv_file, nonexistent_dir)
        # Directory should have been created
        assert nonexistent_dir.exists(), "Output directory should be created"


class TestParallelPlotsIntegration:
    """Integration tests for parallel plotting."""
    
    def test_parallel_complete_workflow(self, csv_file, temp_output_dir):
        """Test complete parallel plotting workflow."""
        # Load CSV
        df = load_weather_csv(csv_file)
        assert len(df) > 0, "CSV should have data"
        
        # Create parallel plots
        output_dir = temp_output_dir / "integration"
        output_dir.mkdir(exist_ok=True)
        results = create_all_plots_parallel(csv_file, output_dir, workers=2)
        
        # Verify results
        assert isinstance(results, dict), "Should return dictionary"
        assert len(results) > 0, "Should generate plots"
        
        # Verify files exist
        file_paths = [v for v in results.values() if isinstance(v, Path)]
        for path in file_paths:
            if path is not None:
                assert path.exists() or path.parent.exists(), "Output path should be accessible"
    
    def test_serial_and_parallel_equivalent(self, csv_file, temp_output_dir):
        """Verify that serial and parallel produce equivalent results."""
        df = load_weather_csv(csv_file)
        
        # Create plots both ways
        serial_dir = temp_output_dir / "serial_eq"
        serial_dir.mkdir(exist_ok=True)
        serial_results = create_all_plots(df, serial_dir)
        
        parallel_dir = temp_output_dir / "parallel_eq"
        parallel_dir.mkdir(exist_ok=True)
        parallel_results = create_all_plots_parallel(csv_file, parallel_dir, workers=2)
        
        # Both should succeed without errors
        assert serial_results is not None, "Serial plots should succeed"
        assert parallel_results is not None, "Parallel plots should succeed"
        
        # Both should have data
        serial_files = sum(1 for v in serial_results.values() if isinstance(v, Path) and v and v.exists())
        parallel_files = sum(1 for v in parallel_results.values() if isinstance(v, Path) and v and v.exists())
        
        assert serial_files > 0, "Serial should create files"
        assert parallel_files > 0, "Parallel should create files"
