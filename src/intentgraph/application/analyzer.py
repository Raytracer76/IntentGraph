"""Repository analysis orchestration."""

import logging
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
from pathlib import Path

from ..adapters.file_repository import FileRepository, FileSystemRepository
from ..adapters.parsers.base import LanguageParser
from ..domain.exceptions import InvalidRepositoryError
from ..domain.models import AnalysisResult, Language
from .services import FileDiscoveryService, CodeAnalysisService, DependencyGraphService, LanguageSummaryService

logger = logging.getLogger(__name__)


class ParserFactory(ABC):
    """Abstract factory for creating language parsers."""
    
    @abstractmethod
    def create_parser(self, language: Language) -> LanguageParser:
        """Create parser for specified language."""
        pass


class DefaultParserFactory(ParserFactory):
    """Default implementation of parser factory."""
    
    def create_parser(self, language: Language) -> LanguageParser:
        """Create parser for specified language."""
        from ..adapters.parsers import get_parser_for_language
        parser = get_parser_for_language(language)
        if parser is None:
            raise ValueError(f"No parser available for language: {language}")
        return parser


class RepositoryAnalyzer:
    """Orchestrates repository analysis using focused services with dependency injection."""

    def __init__(
        self,
        workers: int | None = None,
        include_tests: bool = False,
        language_filter: list[Language] | None = None,
        parser_factory: ParserFactory | None = None,
        file_repository: FileRepository | None = None,
    ) -> None:
        self.workers = workers or cpu_count()
        self.include_tests = include_tests
        self.language_filter = set(language_filter) if language_filter else None
        
        # Dependency injection
        self.parser_factory = parser_factory or DefaultParserFactory()
        self.file_repository = file_repository or FileSystemRepository()
        
        # Initialize services with injected dependencies
        self.file_service = FileDiscoveryService(
            include_tests, 
            self.language_filter,
            self.file_repository
        )
        self.analysis_service = CodeAnalysisService(
            self.parser_factory,
            self.file_repository
        )
        self.graph_service = DependencyGraphService(self.parser_factory)
        self.summary_service = LanguageSummaryService(self.file_repository)

    def analyze(self, repo_path: Path) -> AnalysisResult:
        """Analyze a repository and return results."""
        if not repo_path.exists():
            raise InvalidRepositoryError(f"Repository path does not exist: {repo_path}")

        if not (repo_path / ".git").exists():
            raise InvalidRepositoryError(f"Path is not a Git repository: {repo_path}")

        logger.info(f"Analyzing repository: {repo_path}")

        # Use services for focused operations
        source_files = self.file_service.find_source_files(repo_path)
        logger.info(f"Found {len(source_files)} source files")

        file_infos = self.analysis_service.analyze_files(source_files, repo_path)
        
        self.graph = self.graph_service.build_graph(file_infos, repo_path)
        
        language_summary = self.summary_service.generate_summary(file_infos, source_files)

        return AnalysisResult(
            root=repo_path,
            language_summary=language_summary,
            files=file_infos,
        )
    
    @property 
    def graph(self):
        """Access to dependency graph."""
        return self.graph_service.graph
    
    @graph.setter
    def graph(self, value):
        """Set dependency graph."""
        self.graph_service.graph = value

