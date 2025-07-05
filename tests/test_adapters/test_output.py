import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from intentgraph.adapters.output import OutputFormatter
from intentgraph.domain.models import AnalysisResult, FileInfo, Language, LanguageSummary


class TestOutputAdapter:
    """Test suite for OutputAdapter functionality."""
    
    def test_json_formatting_pretty(self):
        """Test JSON formatting with pretty output."""
        adapter = OutputFormatter()
        result = Mock(spec=AnalysisResult)
        result.dict.return_value = {"test": "data"}
        
        output = adapter.format_json(result, pretty=True)
        
        # Verify pretty formatting
        assert json.loads(output) == {"test": "data"}
        assert len(output.split('\n')) > 1  # Multi-line output
    
    def test_json_formatting_compact(self):
        """Test JSON formatting with compact output."""
        adapter = OutputFormatter()
        result = Mock(spec=AnalysisResult)
        result.dict.return_value = {"test": "data"}
        
        output = adapter.format_json(result, pretty=False)
        
        # Verify compact formatting
        assert json.loads(output) == {"test": "data"}
        assert '\n' not in output  # Single line output
    
    def test_file_export_success(self):
        """Test successful file export."""
        adapter = OutputFormatter()
        result = Mock(spec=AnalysisResult)
        result.dict.return_value = {"test": "data"}
        
        with patch('pathlib.Path.write_text') as mock_write:
            adapter.export_to_file(result, Path("/test/output.json"))
            
            mock_write.assert_called_once()
            written_content = mock_write.call_args[0][0]
            assert json.loads(written_content) == {"test": "data"}
    
    def test_file_export_invalid_path(self):
        """Test file export with invalid path."""
        adapter = OutputFormatter()
        result = Mock(spec=AnalysisResult)
        
        with patch('pathlib.Path.write_text', side_effect=OSError("Permission denied")):
            with pytest.raises(OSError):
                adapter.export_to_file(result, Path("/invalid/path.json"))
    
    def test_schema_validation(self):
        """Test output schema validation."""
        adapter = OutputFormatter()
        
        # Create valid result
        file_info = FileInfo(
            path=Path("test.py"),
            language=Language.PYTHON,
            sha256="abc123",
            loc=10,
            dependencies=[]
        )
        
        result = AnalysisResult(
            root=Path("/test"),
            language_summary={Language.PYTHON: LanguageSummary(file_count=1, total_bytes=100)},
            files=[file_info]
        )
        
        # Test that valid result produces valid JSON
        output = adapter.format_json(result, pretty=True)
        parsed = json.loads(output)
        
        assert "root" in parsed
        assert "language_summary" in parsed
        assert "files" in parsed
        assert isinstance(parsed["files"], list)