"""Test configuration and fixtures."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest
from git import Repo

from intentgraph.domain.models import AnalysisResult, FileInfo, Language


@pytest.fixture
def temp_repo() -> Generator[Path, None, None]:
    """Create a temporary Git repository for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_path = Path(tmp_dir)
        
        # Initialize git repo
        repo = Repo.init(repo_path)
        
        # Create some test files
        (repo_path / "main.py").write_text("""
import utils
from .helpers import helper_func
from submodule import sub_func

def main():
    helper_func()
    sub_func()
""")
        
        (repo_path / "utils.py").write_text("""
def utility_function():
    pass
""")
        
        (repo_path / "helpers.py").write_text("""
def helper_func():
    pass
""")
        
        # Create submodule
        (repo_path / "submodule").mkdir()
        (repo_path / "submodule" / "__init__.py").write_text("""
from .module import sub_func
""")
        
        (repo_path / "submodule" / "module.py").write_text("""
def sub_func():
    pass
""")
        
        # Create .gitignore
        (repo_path / ".gitignore").write_text("""
__pycache__/
*.pyc
.env
""")
        
        # Add files to git
        repo.index.add([
            "main.py", "utils.py", "helpers.py",
            "submodule/__init__.py", "submodule/module.py",
            ".gitignore"
        ])
        repo.index.commit("Initial commit")
        
        yield repo_path


@pytest.fixture
def sample_file_info() -> FileInfo:
    """Create a sample FileInfo for testing."""
    return FileInfo(
        path=Path("test.py"),
        language=Language.PYTHON,
        sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        loc=10,
        dependencies=[],
    )


@pytest.fixture
def sample_analysis_result(sample_file_info: FileInfo) -> AnalysisResult:
    """Create a sample AnalysisResult for testing."""
    return AnalysisResult(
        root=Path("/test/repo"),
        files=[sample_file_info],
    )