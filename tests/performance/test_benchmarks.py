"""Performance benchmarking tests."""

import time
import tempfile
from pathlib import Path

import pytest

from intentgraph.application.analyzer import RepositoryAnalyzer
from intentgraph.application.streaming_analyzer import StreamingAnalyzer, IncrementalAnalyzer


class TestPerformanceBenchmarks:
    """Performance benchmarks for repository analysis."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.repo_dir = self.temp_dir / "test_repo"
        self.repo_dir.mkdir()
        (self.repo_dir / ".git").mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_analysis_speed_benchmarks(self):
        """Benchmark analysis speed across repository sizes."""
        sizes = [10, 50, 100]
        results = {}
        
        for size in sizes:
            # Create repository of specified size
            self._create_test_repository(size)
            
            # Benchmark analysis
            analyzer = RepositoryAnalyzer(workers=2)
            start_time = time.time()
            result = analyzer.analyze(self.repo_dir)
            end_time = time.time()
            
            analysis_time = end_time - start_time
            results[size] = {
                'time': analysis_time,
                'files': len(result.files),
                'rate': len(result.files) / analysis_time if analysis_time > 0 else 0
            }
            
            # Performance assertions
            assert analysis_time < size * 0.1  # Should process ~10 files per second minimum
            assert len(result.files) == size
        
        # Should scale reasonably
        assert results[100]['rate'] >= results[10]['rate'] * 0.5  # Allow for some overhead

    def test_memory_usage_profiling(self):
        """Profile memory usage during analysis."""
        import psutil
        import os
        
        # Create moderately sized repository
        self._create_test_repository(50)
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Run analysis
        analyzer = RepositoryAnalyzer(workers=1)  # Single worker for consistent measurement
        result = analyzer.analyze(self.repo_dir)
        
        # Get peak memory usage
        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory
        
        # Memory usage should be reasonable (< 100MB for 50 files)
        assert memory_increase < 100 * 1024 * 1024  # 100MB
        assert len(result.files) == 50

    def test_concurrent_processing_scaling(self):
        """Test scaling with worker count."""
        self._create_test_repository(100)
        
        worker_counts = [1, 2, 4]
        results = {}
        
        for workers in worker_counts:
            analyzer = RepositoryAnalyzer(workers=workers)
            
            start_time = time.time()
            result = analyzer.analyze(self.repo_dir)
            end_time = time.time()
            
            results[workers] = end_time - start_time
            assert len(result.files) == 100
        
        # More workers should generally be faster (within reason)
        # Allow for overhead and diminishing returns
        assert results[4] <= results[1] * 1.2  # Should be at least not much slower

    def test_streaming_analyzer_performance(self):
        """Test streaming analyzer performance."""
        self._create_test_repository(200)
        
        # Test streaming analyzer
        streaming_analyzer = StreamingAnalyzer(batch_size=50)
        
        start_time = time.time()
        total_files = 0
        for batch in streaming_analyzer.analyze_repository(self.repo_dir):
            total_files += len(batch)
        end_time = time.time()
        
        streaming_time = end_time - start_time
        
        # Compare with regular analyzer
        regular_analyzer = RepositoryAnalyzer()
        start_time = time.time()
        result = regular_analyzer.analyze(self.repo_dir)
        end_time = time.time()
        
        regular_time = end_time - start_time
        
        # Should process same number of files
        assert total_files == len(result.files)
        assert total_files == 200
        
        # Streaming should be competitive (within 50% for this size)
        assert streaming_time <= regular_time * 1.5

    def test_incremental_analysis_performance(self):
        """Test incremental analysis performance."""
        self._create_test_repository(50)
        
        # Initial analysis
        incremental_analyzer = IncrementalAnalyzer()
        start_time = time.time()
        result1 = incremental_analyzer.analyze_changed_files(self.repo_dir)
        end_time = time.time()
        initial_time = end_time - start_time
        
        # Simulate no changes
        start_time = time.time()
        result2 = incremental_analyzer.analyze_changed_files(self.repo_dir)
        end_time = time.time()
        no_change_time = end_time - start_time
        
        # No-change analysis should be much faster
        assert no_change_time < initial_time * 0.1  # Should be at least 10x faster
        assert len(result1.files) == len(result2.files)

    def test_large_file_handling(self):
        """Test handling of large individual files."""
        # Create a large Python file
        large_file = self.repo_dir / "large_module.py"
        
        # Generate a large file with many functions
        content_lines = ['"""Large module for testing."""', '']
        for i in range(1000):
            content_lines.extend([
                f'def function_{i}():',
                f'    """Function {i}."""',
                f'    return {i}',
                '',
            ])
        
        large_file.write_text('\n'.join(content_lines))
        
        # Analyze large file
        analyzer = RepositoryAnalyzer()
        start_time = time.time()
        result = analyzer.analyze(self.repo_dir)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # Should handle large file efficiently
        assert analysis_time < 5.0  # Should complete within 5 seconds
        assert len(result.files) == 1
        
        # Should extract many symbols
        large_file_info = result.files[0]
        assert len(large_file_info.symbols) >= 500  # Should find most functions

    def _create_test_repository(self, file_count: int):
        """Create a test repository with specified number of files."""
        # Clear existing files
        for file in self.repo_dir.glob("*.py"):
            file.unlink()
        
        for i in range(file_count):
            file_path = self.repo_dir / f"module_{i}.py"
            content = f'''
"""Module {i} for testing."""

import os
from pathlib import Path

class TestClass{i}:
    """Test class {i}."""
    
    def __init__(self):
        self.value = {i}
    
    def method_{i}(self):
        """Method {i}."""
        if self.value > 0:
            return self.value * 2
        else:
            return 0

def function_{i}(param: int) -> int:
    """Function {i}."""
    instance = TestClass{i}()
    result = instance.method_{i}()
    
    for j in range(param):
        if j % 2 == 0:
            result += j
        else:
            result -= j
    
    return result

CONSTANT_{i} = {i} * 10
'''
            file_path.write_text(content)