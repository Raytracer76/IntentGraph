"""Tests for domain models."""

import pytest
from pathlib import Path
from datetime import datetime
from uuid import uuid4

from intentgraph.domain.models import FileInfo, Language, AnalysisResult, LanguageSummary


class TestLanguage:
    """Test Language enum."""
    
    def test_from_extension_python(self):
        """Test Python extension detection."""
        assert Language.from_extension(".py") == Language.PYTHON
    
    def test_from_extension_javascript(self):
        """Test JavaScript extension detection."""
        assert Language.from_extension(".js") == Language.JAVASCRIPT
        assert Language.from_extension(".jsx") == Language.JAVASCRIPT
    
    def test_from_extension_typescript(self):
        """Test TypeScript extension detection."""
        assert Language.from_extension(".ts") == Language.TYPESCRIPT
        assert Language.from_extension(".tsx") == Language.TYPESCRIPT
    
    def test_from_extension_go(self):
        """Test Go extension detection."""
        assert Language.from_extension(".go") == Language.GO
    
    def test_from_extension_unknown(self):
        """Test unknown extension."""
        assert Language.from_extension(".txt") == Language.UNKNOWN
        assert Language.from_extension(".rs") == Language.UNKNOWN


class TestFileInfo:
    """Test FileInfo model."""
    
    def test_from_path_creates_valid_file_info(self, tmp_path):
        """Test FileInfo creation from path."""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')\n# comment\n\n")
        
        file_info = FileInfo.from_path(test_file, tmp_path)
        
        assert file_info.path == Path("test.py")
        assert file_info.language == Language.PYTHON
        assert file_info.loc == 1  # Only count non-empty, non-comment lines
        assert len(file_info.sha256) == 64
        assert file_info.dependencies == []
    
    def test_from_path_handles_unicode_decode_error(self, tmp_path):
        """Test handling of binary files."""
        # Create binary file
        binary_file = tmp_path / "binary.py"
        binary_file.write_bytes(b'\x00\x01\x02\x03')
        
        file_info = FileInfo.from_path(binary_file, tmp_path)
        
        assert file_info.loc == 0
        assert file_info.language == Language.PYTHON


class TestAnalysisResult:
    """Test AnalysisResult model."""
    
    def test_analysis_result_creation(self):
        """Test AnalysisResult creation."""
        result = AnalysisResult(root=Path("/test"))
        
        assert result.root == Path("/test")
        assert isinstance(result.analyzed_at, datetime)
        assert result.language_summary == {}
        assert result.files == []
    
    def test_analysis_result_with_files(self, sample_file_info):
        """Test AnalysisResult with files."""
        result = AnalysisResult(
            root=Path("/test"),
            files=[sample_file_info]
        )
        
        assert len(result.files) == 1
        assert result.files[0] == sample_file_info


class TestLanguageSummary:
    """Test LanguageSummary model."""
    
    def test_language_summary_creation(self):
        """Test LanguageSummary creation."""
        summary = LanguageSummary(file_count=5, total_bytes=1024)
        
        assert summary.file_count == 5
        assert summary.total_bytes == 1024
    
    def test_language_summary_validation(self):
        """Test LanguageSummary validation."""
        with pytest.raises(ValueError):
            LanguageSummary(file_count=-1, total_bytes=1024)
        
        with pytest.raises(ValueError):
            LanguageSummary(file_count=5, total_bytes=-1)