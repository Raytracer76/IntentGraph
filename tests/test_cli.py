"""Tests for CLI interface."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from intentgraph.cli import app
from intentgraph.domain.models import AnalysisResult


class TestCLI:
    """Test CLI interface."""
    
    def test_help_message(self):
        """Test help message."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "intentgraph" in result.output
        assert "dependency analyzer" in result.output
    
    def test_analyze_command_help(self):
        """Test analyze command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["analyze", "--help"])
        
        assert result.exit_code == 0
        assert "--output" in result.output
        assert "--lang" in result.output
        assert "--include-tests" in result.output
    
    @patch('intentgraph.application.analyzer.RepositoryAnalyzer')
    def test_analyze_command_success(self, mock_analyzer, temp_repo):
        """Test successful analysis."""
        # Mock analyzer
        mock_instance = Mock()
        mock_analyzer.return_value = mock_instance
        
        # Mock result
        mock_result = AnalysisResult(root=temp_repo)
        mock_instance.analyze.return_value = mock_result
        mock_instance.graph.find_cycles.return_value = []
        mock_instance.graph.get_stats.return_value = {
            "nodes": 5, "edges": 3, "cycles": 0, "components": 1
        }
        
        runner = CliRunner()
        result = runner.invoke(app, ["analyze", str(temp_repo)])
        
        assert result.exit_code == 0
        assert mock_instance.analyze.called
    
    @patch('intentgraph.application.analyzer.RepositoryAnalyzer')
    def test_analyze_with_output_file(self, mock_analyzer, temp_repo, tmp_path):
        """Test analysis with output file."""
        # Mock analyzer
        mock_instance = Mock()
        mock_analyzer.return_value = mock_instance
        
        mock_result = AnalysisResult(root=temp_repo)
        mock_instance.analyze.return_value = mock_result
        mock_instance.graph.find_cycles.return_value = []
        mock_instance.graph.get_stats.return_value = {
            "nodes": 5, "edges": 3, "cycles": 0, "components": 1
        }
        
        output_file = tmp_path / "output.json"
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "analyze", str(temp_repo),
            "--output", str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
    
    @patch('intentgraph.application.analyzer.RepositoryAnalyzer')
    def test_analyze_with_cycles_exit_code(self, mock_analyzer, temp_repo):
        """Test analysis with cycles returns exit code 2."""
        # Mock analyzer with cycles
        mock_instance = Mock()
        mock_analyzer.return_value = mock_instance
        
        mock_result = AnalysisResult(root=temp_repo)
        mock_instance.analyze.return_value = mock_result
        mock_instance.graph.find_cycles.return_value = [['file1', 'file2']]
        mock_instance.graph.get_file_info.return_value = Mock(path=Path("test.py"))
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "analyze", str(temp_repo),
            "--show-cycles"
        ])
        
        assert result.exit_code == 2
    
    def test_analyze_nonexistent_repo(self):
        """Test analysis of non-existent repository."""
        runner = CliRunner()
        result = runner.invoke(app, ["analyze", "/nonexistent/path"])
        
        assert result.exit_code == 2  # Path doesn't exist