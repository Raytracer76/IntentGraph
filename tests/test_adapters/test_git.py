"""Tests for Git integration."""

import pytest
from pathlib import Path

from intentgraph.adapters.git import GitIgnoreHandler


class TestGitIgnoreHandler:
    """Test GitIgnoreHandler class."""
    
    def test_load_gitignore(self, temp_repo):
        """Test loading .gitignore files."""
        handler = GitIgnoreHandler()
        handler.load_gitignore(temp_repo)
        
        assert handler._spec is not None
        assert handler._repo_path == temp_repo
    
    def test_is_ignored_basic(self, temp_repo):
        """Test basic ignore functionality."""
        handler = GitIgnoreHandler()
        handler.load_gitignore(temp_repo)
        
        # Create test files
        (temp_repo / "__pycache__").mkdir()
        (temp_repo / "__pycache__" / "test.pyc").touch()
        (temp_repo / "normal.py").touch()
        
        # Test ignoring
        assert handler.is_ignored(temp_repo / "__pycache__" / "test.pyc", temp_repo)
        assert not handler.is_ignored(temp_repo / "normal.py", temp_repo)
    
    def test_is_ignored_custom_patterns(self, temp_repo):
        """Test custom ignore patterns."""
        # Add custom patterns to .gitignore
        gitignore = temp_repo / ".gitignore"
        gitignore.write_text(gitignore.read_text() + "\n*.log\ntemp/\n")
        
        handler = GitIgnoreHandler()
        handler.load_gitignore(temp_repo)
        
        # Create test files
        (temp_repo / "debug.log").touch()
        (temp_repo / "temp").mkdir()
        (temp_repo / "temp" / "file.txt").touch()
        
        assert handler.is_ignored(temp_repo / "debug.log", temp_repo)
        assert handler.is_ignored(temp_repo / "temp" / "file.txt", temp_repo)
    
    def test_nested_gitignore(self, temp_repo):
        """Test nested .gitignore files."""
        # Create nested directory with .gitignore
        nested_dir = temp_repo / "nested"
        nested_dir.mkdir()
        (nested_dir / ".gitignore").write_text("*.tmp\n")
        
        handler = GitIgnoreHandler()
        handler.load_gitignore(temp_repo)
        
        # Create test files
        (nested_dir / "test.tmp").touch()
        (nested_dir / "test.py").touch()
        
        assert handler.is_ignored(nested_dir / "test.tmp", temp_repo)
        assert not handler.is_ignored(nested_dir / "test.py", temp_repo)