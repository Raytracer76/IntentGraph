"""End-to-end integration tests for full workflow."""

import tempfile
from pathlib import Path

import pytest

from src.intentgraph.application.analyzer import RepositoryAnalyzer
from src.intentgraph.domain.models import Language


class TestEndToEndWorkflows:
    """Test complete repository analysis workflows."""

    def setup_method(self):
        """Set up test repository."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.repo_dir = self.temp_dir / "test_repo"
        self.repo_dir.mkdir()
        
        # Create minimal git repo
        (self.repo_dir / ".git").mkdir()
        (self.repo_dir / ".git" / "config").write_text("[core]\n")

    def teardown_method(self):
        """Clean up test repository."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_repository_analysis(self):
        """Test complete repository analysis workflow."""
        # Create test Python files
        (self.repo_dir / "main.py").write_text('''
"""Main module."""

from utils import helper_function

def main():
    """Main function."""
    result = helper_function("test")
    return result

if __name__ == "__main__":
    main()
''')
        
        (self.repo_dir / "utils.py").write_text('''
"""Utility functions."""

def helper_function(value: str) -> str:
    """Helper function."""
    return f"processed: {value}"

class UtilityClass:
    """Utility class."""
    
    def process(self, data):
        return data.upper()
''')
        
        # Run analysis
        analyzer = RepositoryAnalyzer()
        result = analyzer.analyze(self.repo_dir)
        
        # Verify results
        assert result.root == self.repo_dir
        assert len(result.files) == 2
        assert Language.PYTHON in result.language_summary
        
        # Check file analysis
        file_paths = [str(f.path) for f in result.files]
        assert "main.py" in file_paths
        assert "utils.py" in file_paths
        
        # Check dependency detection
        main_file = next(f for f in result.files if f.path.name == "main.py")
        assert len(main_file.symbols) > 0
        assert any(s.name == "main" for s in main_file.symbols)

    def test_multi_language_repository(self):
        """Test mixed-language repository analysis."""
        # Create Python file
        (self.repo_dir / "app.py").write_text('''
def greet(name: str) -> str:
    return f"Hello, {name}!"
''')
        
        # Create Go file
        (self.repo_dir / "main.go").write_text('''
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
''')
        
        # Create JavaScript file
        (self.repo_dir / "script.js").write_text('''
function greet(name) {
    return `Hello, ${name}!`;
}

module.exports = { greet };
''')
        
        # Run analysis
        analyzer = RepositoryAnalyzer()
        result = analyzer.analyze(self.repo_dir)
        
        # Verify multiple languages detected
        assert len(result.language_summary) >= 2  # Python and JS at minimum
        
        # Check file count
        assert len(result.files) == 3

    def test_cli_integration_comprehensive(self):
        """Test full CLI functionality."""
        # Create test file
        (self.repo_dir / "test_module.py").write_text('''
"""Test module for CLI testing."""

class TestClass:
    """Test class."""
    
    def test_method(self):
        """Test method."""
        return "test"

def test_function():
    """Test function."""
    return TestClass().test_method()

CONSTANT = "test_value"
''')
        
        # Test analyzer directly (simulating CLI usage)
        analyzer = RepositoryAnalyzer(
            workers=1,
            include_tests=True,
            language_filter=[Language.PYTHON]
        )
        
        result = analyzer.analyze(self.repo_dir)
        
        # Verify CLI-style results
        assert result is not None
        assert len(result.files) == 1
        assert result.language_summary[Language.PYTHON].file_count == 1
        
        # Check symbols were extracted
        test_file = result.files[0]
        symbol_names = [s.name for s in test_file.symbols]
        assert "TestClass" in symbol_names
        assert "test_function" in symbol_names
        assert "CONSTANT" in symbol_names

    def test_error_handling_invalid_repository(self):
        """Test error handling for invalid repositories."""
        invalid_repo = self.temp_dir / "invalid"
        invalid_repo.mkdir()
        # No .git directory
        
        analyzer = RepositoryAnalyzer()
        
        with pytest.raises(Exception):  # Should raise InvalidRepositoryError
            analyzer.analyze(invalid_repo)

    def test_gitignore_integration(self):
        """Test gitignore file integration."""
        # Create gitignore
        (self.repo_dir / ".gitignore").write_text('''
*.pyc
__pycache__/
.venv/
ignored.py
''')
        
        # Create files
        (self.repo_dir / "main.py").write_text("# Main file")
        (self.repo_dir / "ignored.py").write_text("# Ignored file")
        (self.repo_dir / "__pycache__").mkdir()
        (self.repo_dir / "__pycache__" / "main.pyc").write_text("bytecode")
        
        # Run analysis
        analyzer = RepositoryAnalyzer()
        result = analyzer.analyze(self.repo_dir)
        
        # Should only find main.py
        file_names = [f.path.name for f in result.files]
        assert "main.py" in file_names
        assert "ignored.py" not in file_names
        assert "main.pyc" not in file_names

    def test_test_file_filtering(self):
        """Test test file filtering functionality."""
        # Create regular and test files
        (self.repo_dir / "main.py").write_text("# Main module")
        (self.repo_dir / "test_main.py").write_text("# Test file")
        (self.repo_dir / "main_test.py").write_text("# Another test file")
        (self.repo_dir / "tests").mkdir()
        (self.repo_dir / "tests" / "test_utils.py").write_text("# Test utilities")
        
        # Test without including tests
        analyzer = RepositoryAnalyzer(include_tests=False)
        result = analyzer.analyze(self.repo_dir)
        
        file_names = [f.path.name for f in result.files]
        assert "main.py" in file_names
        assert "test_main.py" not in file_names
        assert "main_test.py" not in file_names
        assert "test_utils.py" not in file_names
        
        # Test with including tests
        analyzer_with_tests = RepositoryAnalyzer(include_tests=True)
        result_with_tests = analyzer_with_tests.analyze(self.repo_dir)
        
        assert len(result_with_tests.files) > len(result.files)

    def test_language_filtering(self):
        """Test language filtering functionality."""
        # Create multiple language files
        (self.repo_dir / "app.py").write_text("# Python file")
        (self.repo_dir / "script.js").write_text("// JavaScript file")
        (self.repo_dir / "main.go").write_text("// Go file")
        
        # Test Python-only filtering
        analyzer = RepositoryAnalyzer(language_filter=[Language.PYTHON])
        result = analyzer.analyze(self.repo_dir)
        
        assert len(result.files) == 1
        assert result.files[0].language == Language.PYTHON
        assert Language.PYTHON in result.language_summary
        assert Language.JAVASCRIPT not in result.language_summary

    def test_dependency_graph_building(self):
        """Test dependency graph building."""
        # Create files with dependencies
        (self.repo_dir / "module_a.py").write_text('''
from module_b import function_b

def function_a():
    return function_b() + " from A"
''')
        
        (self.repo_dir / "module_b.py").write_text('''
def function_b():
    return "Hello from B"
''')
        
        # Run analysis
        analyzer = RepositoryAnalyzer()
        result = analyzer.analyze(self.repo_dir)
        
        # Check dependency graph
        stats = analyzer.graph.get_stats()
        assert stats["nodes"] >= 2
        
        # Should detect dependency from module_a to module_b
        module_a = next(f for f in result.files if f.path.name == "module_a.py")
        assert len(module_a.dependencies) > 0 or len(module_a.imports) > 0

    def test_performance_with_larger_repository(self):
        """Test performance with moderately sized repository."""
        import time
        
        # Create multiple files
        for i in range(10):
            (self.repo_dir / f"module_{i}.py").write_text(f'''
"""Module {i}."""

class Class{i}:
    """Class {i}."""
    
    def method_{i}(self):
        """Method {i}."""
        return {i}

def function_{i}():
    """Function {i}."""
    return Class{i}().method_{i}()

CONSTANT_{i} = {i}
''')
        
        # Measure analysis time
        analyzer = RepositoryAnalyzer(workers=2)
        start_time = time.time()
        result = analyzer.analyze(self.repo_dir)
        end_time = time.time()
        
        # Should complete reasonably quickly
        analysis_time = end_time - start_time
        assert analysis_time < 10.0  # Should complete in under 10 seconds
        
        # Should analyze all files
        assert len(result.files) == 10
        
        # Should extract symbols from all files
        total_symbols = sum(len(f.symbols) for f in result.files)
        assert total_symbols >= 30  # At least 3 symbols per file