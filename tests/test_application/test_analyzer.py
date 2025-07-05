import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from intentgraph.application.analyzer import RepositoryAnalyzer
from intentgraph.domain.models import Language, FileInfo
from intentgraph.domain.exceptions import InvalidRepositoryError


class TestRepositoryAnalyzer:
    """Test suite for RepositoryAnalyzer functionality."""
    
    def test_invalid_repository_handling(self):
        """Test handling of invalid repository paths."""
        analyzer = RepositoryAnalyzer()
        
        with pytest.raises(InvalidRepositoryError):
            analyzer.analyze(Path("/nonexistent/path"))
    
    def test_parallel_worker_configuration(self):
        """Test parallel worker configuration."""
        analyzer = RepositoryAnalyzer(workers=4)
        assert analyzer.workers == 4
        
        # Test auto-detection
        analyzer_auto = RepositoryAnalyzer(workers=0)
        assert analyzer_auto.workers > 0
    
    def test_language_filter_validation(self):
        """Test language filter functionality."""
        analyzer = RepositoryAnalyzer(language_filter={Language.PYTHON})
        
        # Mock file discovery
        with patch.object(analyzer, '_find_source_files') as mock_find:
            mock_find.return_value = [
                Path("test.py"),
                Path("test.js"),
                Path("test.go")
            ]
            
            with patch.object(analyzer, '_analyze_single_file') as mock_analyze:
                mock_analyze.return_value = None
                
                # Should only analyze Python files
                analyzer.analyze(Path("/test/repo"))
                
                # Verify only Python files were processed
                analyzed_files = [call[0][0] for call in mock_analyze.call_args_list]
                assert Path("test.py") in analyzed_files
                assert Path("test.js") not in analyzed_files
                assert Path("test.go") not in analyzed_files
    
    def test_file_discovery_logic(self):
        """Test file discovery with gitignore integration."""
        analyzer = RepositoryAnalyzer()
        
        with patch('pathlib.Path.rglob') as mock_rglob:
            mock_rglob.return_value = [
                Path("src/main.py"),
                Path("node_modules/package.js"),
                Path("__pycache__/cache.pyc")
            ]
            
            with patch.object(analyzer, '_should_ignore_file') as mock_ignore:
                mock_ignore.side_effect = lambda x: "node_modules" in str(x) or "__pycache__" in str(x)
                
                files = analyzer._find_source_files(Path("/test/repo"))
                
                assert Path("src/main.py") in files
                assert len([f for f in files if "node_modules" in str(f)]) == 0
                assert len([f for f in files if "__pycache__" in str(f)]) == 0
    
    def test_dependency_graph_construction(self):
        """Test dependency graph construction."""
        analyzer = RepositoryAnalyzer()
        
        # Mock file analysis results
        file1 = FileInfo(
            path=Path("src/main.py"),
            language=Language.PYTHON,
            sha256="abc123",
            loc=10,
            dependencies=[]
        )
        
        file2 = FileInfo(
            path=Path("src/utils.py"),
            language=Language.PYTHON,
            sha256="def456",
            loc=5,
            dependencies=[]
        )
        
        with patch.object(analyzer, '_find_source_files') as mock_find:
            mock_find.return_value = [file1.path, file2.path]
            
            with patch.object(analyzer, '_analyze_single_file') as mock_analyze:
                mock_analyze.side_effect = [file1, file2]
                
                result = analyzer.analyze(Path("/test/repo"))
                
                assert len(result.files) == 2
                assert file1 in result.files
                assert file2 in result.files
    
    def test_error_handling_and_logging(self):
        """Test error handling and logging."""
        analyzer = RepositoryAnalyzer()
        
        with patch.object(analyzer, '_find_source_files') as mock_find:
            mock_find.return_value = [Path("test.py")]
            
            with patch.object(analyzer, '_analyze_single_file') as mock_analyze:
                mock_analyze.side_effect = Exception("Parse error")
                
                with patch('intentgraph.application.analyzer.logger') as mock_logger:
                    result = analyzer.analyze(Path("/test/repo"))
                    
                    # Should log error and continue
                    mock_logger.warning.assert_called()
                    assert len(result.files) == 0  # No files due to error