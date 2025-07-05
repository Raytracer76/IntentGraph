"""Tests for dependency graph operations."""

import pytest
from pathlib import Path
from uuid import uuid4

from intentgraph.domain.graph import DependencyGraph
from intentgraph.domain.models import FileInfo, Language


class TestDependencyGraph:
    """Test DependencyGraph class."""
    
    def test_add_file(self):
        """Test adding files to graph."""
        graph = DependencyGraph()
        file_info = FileInfo(
            path=Path("test.py"),
            language=Language.PYTHON,
            sha256="abc123",
            loc=10,
        )
        
        graph.add_file(file_info)
        
        assert file_info.id in graph._file_map
        assert graph._graph.has_node(file_info.id)
    
    def test_add_dependency(self):
        """Test adding dependencies."""
        graph = DependencyGraph()
        
        file1 = FileInfo(
            path=Path("file1.py"),
            language=Language.PYTHON,
            sha256="abc123",
            loc=10,
        )
        file2 = FileInfo(
            path=Path("file2.py"),
            language=Language.PYTHON,
            sha256="def456",
            loc=5,
        )
        
        graph.add_file(file1)
        graph.add_file(file2)
        graph.add_dependency(file1.id, file2.id)
        
        assert graph._graph.has_edge(file1.id, file2.id)
        assert file2.id in graph.get_dependencies(file1.id)
    
    def test_find_cycles_no_cycles(self):
        """Test cycle detection with no cycles."""
        graph = DependencyGraph()
        
        file1 = FileInfo(path=Path("file1.py"), language=Language.PYTHON, sha256="abc", loc=1)
        file2 = FileInfo(path=Path("file2.py"), language=Language.PYTHON, sha256="def", loc=1)
        
        graph.add_file(file1)
        graph.add_file(file2)
        graph.add_dependency(file1.id, file2.id)
        
        cycles = graph.find_cycles()
        assert cycles == []
    
    def test_find_cycles_with_cycles(self):
        """Test cycle detection with cycles."""
        graph = DependencyGraph()
        
        file1 = FileInfo(path=Path("file1.py"), language=Language.PYTHON, sha256="abc", loc=1)
        file2 = FileInfo(path=Path("file2.py"), language=Language.PYTHON, sha256="def", loc=1)
        
        graph.add_file(file1)
        graph.add_file(file2)
        graph.add_dependency(file1.id, file2.id)
        graph.add_dependency(file2.id, file1.id)
        
        cycles = graph.find_cycles()
        assert len(cycles) > 0
    
    def test_topological_sort(self):
        """Test topological sorting."""
        graph = DependencyGraph()
        
        file1 = FileInfo(path=Path("file1.py"), language=Language.PYTHON, sha256="abc", loc=1)
        file2 = FileInfo(path=Path("file2.py"), language=Language.PYTHON, sha256="def", loc=1)
        file3 = FileInfo(path=Path("file3.py"), language=Language.PYTHON, sha256="ghi", loc=1)
        
        graph.add_file(file1)
        graph.add_file(file2)
        graph.add_file(file3)
        
        # file1 -> file2 -> file3
        graph.add_dependency(file1.id, file2.id)
        graph.add_dependency(file2.id, file3.id)
        
        sorted_files = graph.topological_sort()
        
        # file3 should come before file2, file2 before file1
        assert sorted_files.index(file3.id) < sorted_files.index(file2.id)
        assert sorted_files.index(file2.id) < sorted_files.index(file1.id)
    
    def test_get_stats(self):
        """Test graph statistics."""
        graph = DependencyGraph()
        
        file1 = FileInfo(path=Path("file1.py"), language=Language.PYTHON, sha256="abc", loc=1)
        file2 = FileInfo(path=Path("file2.py"), language=Language.PYTHON, sha256="def", loc=1)
        
        graph.add_file(file1)
        graph.add_file(file2)
        graph.add_dependency(file1.id, file2.id)
        
        stats = graph.get_stats()
        
        assert stats["nodes"] == 2
        assert stats["edges"] == 1
        assert stats["cycles"] == 0
        assert stats["components"] == 1