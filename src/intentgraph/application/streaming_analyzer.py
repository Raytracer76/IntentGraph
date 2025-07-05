"""Streaming analysis for large repositories."""

import logging
from pathlib import Path
from typing import Iterator, List

from ..domain.models import FileInfo, AnalysisResult, Language
from .analyzer import RepositoryAnalyzer

logger = logging.getLogger(__name__)


class StreamingAnalyzer:
    """Analyzer optimized for large repositories with streaming processing."""
    
    def __init__(self, batch_size: int = 100, **analyzer_kwargs):
        self.batch_size = batch_size
        self.analyzer = RepositoryAnalyzer(**analyzer_kwargs)
    
    def analyze_repository(self, repo_path: Path) -> Iterator[List[FileInfo]]:
        """Process files in batches instead of loading all at once."""
        # Validate repository
        if not repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        if not (repo_path / ".git").exists():
            raise ValueError(f"Path is not a Git repository: {repo_path}")
        
        # Find all source files
        source_files = self.analyzer.file_service.find_source_files(repo_path)
        logger.info(f"Found {len(source_files)} source files for streaming analysis")
        
        # Process in batches
        for batch in self._get_file_batches(source_files, self.batch_size):
            batch_results = self.analyzer.analysis_service.analyze_files(batch, repo_path)
            yield batch_results
            # Explicitly free memory
            del batch_results
    
    def _get_file_batches(self, files: List[Path], batch_size: int) -> Iterator[List[Path]]:
        """Split files into batches for processing."""
        for i in range(0, len(files), batch_size):
            yield files[i:i + batch_size]


class IncrementalAnalyzer:
    """Analyzer with incremental analysis based on file timestamps."""
    
    def __init__(self, **analyzer_kwargs):
        self.analyzer = RepositoryAnalyzer(**analyzer_kwargs)
        self.file_timestamps = {}
        self.analysis_cache = {}
    
    def analyze_changed_files(self, repo_path: Path) -> AnalysisResult:
        """Analyze only files that have changed since last analysis."""
        # Detect changes
        changed_files = self._detect_changes(repo_path)
        logger.info(f"Detected {len(changed_files)} changed files")
        
        if not changed_files:
            logger.info("No changes detected, using cached results")
            return self._get_cached_results(repo_path)
        
        # Analyze only changed files
        changed_file_infos = self.analyzer.analysis_service.analyze_files(changed_files, repo_path)
        
        # Update cache
        for file_info in changed_file_infos:
            self.analysis_cache[str(file_info.path)] = file_info
        
        # Update dependency graph incrementally
        self._update_dependency_graph(changed_files, repo_path)
        
        # Generate updated results
        all_file_infos = list(self.analysis_cache.values())
        language_summary = self.analyzer.summary_service.generate_summary(all_file_infos, list(self.analysis_cache.keys()))
        
        return AnalysisResult(
            root=repo_path,
            language_summary=language_summary,
            files=all_file_infos,
        )
    
    def _detect_changes(self, repo_path: Path) -> List[Path]:
        """Detect files that have changed since last analysis."""
        changed_files = []
        source_files = self.analyzer.file_service.find_source_files(repo_path)
        
        for file_path in source_files:
            try:
                current_mtime = file_path.stat().st_mtime
                cached_mtime = self.file_timestamps.get(str(file_path))
                
                if cached_mtime is None or current_mtime > cached_mtime:
                    changed_files.append(file_path)
                    self.file_timestamps[str(file_path)] = current_mtime
                    
            except OSError:
                # File might have been deleted
                continue
        
        return changed_files
    
    def _update_dependency_graph(self, changed_files: List[Path], repo_path: Path):
        """Update dependency graph for changed files only."""
        # For now, rebuild the entire graph
        # In a production system, you'd want more sophisticated incremental updates
        all_file_infos = list(self.analysis_cache.values())
        self.analyzer.graph = self.analyzer.graph_service.build_graph(all_file_infos, repo_path)
    
    def _get_cached_results(self, repo_path: Path) -> AnalysisResult:
        """Get results from cache."""
        all_file_infos = list(self.analysis_cache.values())
        language_summary = self.analyzer.summary_service.generate_summary(all_file_infos, list(self.analysis_cache.keys()))
        
        return AnalysisResult(
            root=repo_path,
            language_summary=language_summary,
            files=all_file_infos,
        )