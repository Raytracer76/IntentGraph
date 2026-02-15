"""Refactored services for repository analysis."""

import logging
from pathlib import Path
from typing import Optional

from ..adapters.git import GitIgnoreHandler
from ..adapters.parsers import get_parser_for_language
from ..domain.exceptions import InvalidRepositoryError
from ..domain.graph import DependencyGraph
from ..domain.models import AnalysisResult, FileInfo, Language, LanguageSummary

logger = logging.getLogger(__name__)


class FileDiscoveryService:
    """Service for discovering source files in repositories."""
    
    def __init__(self, include_tests: bool = False, language_filter: set[Language] | None = None, file_repository=None):
        self.include_tests = include_tests
        self.language_filter = language_filter
        self.file_repository = file_repository
        self._git_handler = GitIgnoreHandler()
    
    def find_source_files(self, repo_path: Path) -> list[Path]:
        """Find all source files in the repository."""
        self._git_handler.load_gitignore(repo_path)
        source_files = []

        for file_path in repo_path.rglob("*"):
            try:
                if not file_path.is_file():
                    continue
            except (OSError, PermissionError):
                continue

            if self._git_handler.is_ignored(file_path, repo_path):
                continue

            if not self.include_tests and self._is_test_file(file_path):
                continue

            language = Language.from_extension(file_path.suffix)
            if language == Language.UNKNOWN:
                continue

            if self.language_filter and language not in self.language_filter:
                continue

            source_files.append(file_path)

        return source_files
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        path_str = str(file_path).lower()
        return (
            "test" in path_str or
            "spec" in path_str or
            file_path.name.startswith("test_") or
            file_path.name.endswith("_test.py") or
            file_path.name.endswith(".test.js") or
            file_path.name.endswith(".test.ts") or
            file_path.name.endswith(".spec.js") or
            file_path.name.endswith(".spec.ts")
        )


class CodeAnalysisService:
    """Service for analyzing individual files and extracting metadata."""
    
    def __init__(self, parser_factory=None, file_repository=None):
        self.parser_factory = parser_factory
        self.file_repository = file_repository
    
    def analyze_files(self, files: list[Path], repo_path: Path) -> list[FileInfo]:
        """Analyze files to extract metadata."""
        file_infos = []
        
        for file_path in files:
            try:
                file_info = self._analyze_single_file(file_path, repo_path)
                if file_info:
                    file_infos.append(file_info)
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")
                
        return file_infos
    
    def _analyze_single_file(self, file_path: Path, repo_path: Path) -> Optional[FileInfo]:
        """Analyze a single file with enhanced structure analysis."""
        try:
            basic_info = FileInfo.from_path(file_path, repo_path)
            
            if basic_info.language == Language.PYTHON:
                from ..adapters.parsers.enhanced_python_parser import EnhancedPythonParser
                parser = EnhancedPythonParser()

                symbols, exports, func_deps, imports, metadata = parser.extract_code_structure(
                    file_path, repo_path
                )

                file_purpose = self._infer_file_purpose(basic_info.path, symbols)
                key_abstractions = self._extract_key_abstractions(symbols)
                design_patterns = self._detect_design_patterns(symbols, exports)

                return FileInfo(
                    path=basic_info.path,
                    language=basic_info.language,
                    sha256=basic_info.sha256,
                    loc=basic_info.loc,
                    id=basic_info.id,
                    dependencies=basic_info.dependencies,
                    symbols=symbols,
                    exports=exports,
                    function_dependencies=func_deps,
                    imports=imports,
                    complexity_score=metadata.get("complexity_score", 0),
                    maintainability_index=metadata.get("maintainability_index", 0.0),
                    file_purpose=file_purpose,
                    key_abstractions=key_abstractions,
                    design_patterns=design_patterns
                )
            elif basic_info.language in (Language.TYPESCRIPT, Language.JAVASCRIPT):
                from ..adapters.parsers.typescript_parser import TypeScriptParser
                from ..adapters.parsers.javascript_parser import JavaScriptParser

                # Select appropriate parser
                if basic_info.language == Language.TYPESCRIPT:
                    parser = TypeScriptParser()
                else:
                    parser = JavaScriptParser()

                symbols, exports, func_deps, imports, metadata = parser.extract_code_structure(
                    file_path, repo_path
                )

                file_purpose = self._infer_file_purpose(basic_info.path, symbols)

                return FileInfo(
                    path=basic_info.path,
                    language=basic_info.language,
                    sha256=basic_info.sha256,
                    loc=basic_info.loc,
                    id=basic_info.id,
                    dependencies=basic_info.dependencies,
                    symbols=symbols,
                    exports=exports,
                    function_dependencies=func_deps,
                    imports=imports,
                    complexity_score=metadata.get("total_functions", 0) + metadata.get("total_classes", 0),
                    maintainability_index=0.0,  # Not calculated for TS/JS yet
                    file_purpose=file_purpose,
                    key_abstractions=[],  # Not extracted for TS/JS yet
                    design_patterns=[]  # Not detected for TS/JS yet
                )
            else:
                return basic_info
                
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")
            return None
    
    def _infer_file_purpose(self, file_path: Path, symbols: list) -> str:
        """Infer the purpose of a file from its path and symbols."""
        path_str = str(file_path).lower()
        
        if "test" in path_str:
            return "testing"
        elif "cli" in path_str or "main" in path_str:
            return "command_line_interface"
        elif "models" in path_str or "model" in path_str:
            return "data_models"
        elif "parser" in path_str:
            return "parsing"
        elif "adapter" in path_str:
            return "external_interface"
        elif "exception" in path_str or "error" in path_str:
            return "error_handling"
        elif "__init__" in path_str:
            return "package_initialization"
        elif "config" in path_str or "setting" in path_str:
            return "configuration"
        elif "util" in path_str or "helper" in path_str:
            return "utilities"
        
        if not symbols:
            return "unknown"
            
        class_count = len([s for s in symbols if s.symbol_type == "class"])
        function_count = len([s for s in symbols if s.symbol_type in ("function", "async_function")])
        
        if class_count > function_count:
            return "class_definitions"
        elif function_count > 0:
            return "functional_logic"
        else:
            return "configuration_or_constants"
    
    def _extract_key_abstractions(self, symbols: list) -> list[str]:
        """Extract key abstractions from symbols."""
        abstractions = []
        
        for symbol in symbols:
            if symbol.symbol_type == "class" and symbol.is_exported:
                abstractions.append(symbol.name)
            elif symbol.symbol_type in ("function", "async_function") and symbol.is_exported:
                if symbol.docstring or symbol.decorators:
                    abstractions.append(symbol.name)
                    
        return abstractions[:5]
    
    def _detect_design_patterns(self, symbols: list, exports: list) -> list[str]:
        """Detect common design patterns in the code."""
        patterns = []
        class_names = [s.name for s in symbols if s.symbol_type == "class"]
        
        pattern_keywords = {
            "factory": "Factory",
            "parser": "Parser", 
            "adapter": "Adapter",
            "builder": "Builder",
            "observer": ["Observer", "Listener"],
            "command": "Command",
            "strategy": "Strategy"
        }
        
        for pattern, keywords in pattern_keywords.items():
            if isinstance(keywords, list):
                if any(keyword in name for name in class_names for keyword in keywords):
                    patterns.append(pattern)
            else:
                if any(keywords in name for name in class_names):
                    patterns.append(pattern)
                    
        return patterns


class DependencyGraphService:
    """Service for building dependency graphs from file information."""
    
    def __init__(self, parser_factory=None):
        self.graph = DependencyGraph()
        self.parser_factory = parser_factory
    
    def build_graph(self, file_infos: list[FileInfo], repo_path: Path) -> DependencyGraph:
        """Build dependency graph between files."""
        # Add all files to graph
        for file_info in file_infos:
            self.graph.add_file(file_info)
        
        # Create mapping from path to file info
        path_to_file = {str(f.path): f for f in file_infos}

        for file_info in file_infos:
            parser = get_parser_for_language(file_info.language)
            if not parser:
                continue

            try:
                full_path = repo_path / file_info.path
                dependencies = parser.extract_dependencies(full_path, repo_path)

                dependency_ids = []
                for dep_path in dependencies:
                    if dep_path in path_to_file:
                        dependency_ids.append(path_to_file[dep_path].id)
                        self.graph.add_dependency(file_info.id, path_to_file[dep_path].id)

                file_info.dependencies.extend(dependency_ids)

            except Exception as e:
                logger.warning(f"Failed to extract dependencies for {file_info.path}: {e}")
        
        return self.graph


class LanguageSummaryService:
    """Service for generating language summaries."""
    
    def __init__(self, file_repository=None):
        self.file_repository = file_repository
    
    def generate_summary(self, file_infos: list[FileInfo], source_files: list[Path]) -> dict[Language, LanguageSummary]:
        """Generate language summary statistics."""
        summary = {}
        language_counts = {}
        language_bytes = {}

        for file_path in source_files:
            language = Language.from_extension(file_path.suffix)
            if language == Language.UNKNOWN:
                continue

            language_counts[language] = language_counts.get(language, 0) + 1

            try:
                file_size = file_path.stat().st_size
                language_bytes[language] = language_bytes.get(language, 0) + file_size
            except Exception:
                pass

        for language in language_counts:
            summary[language] = LanguageSummary(
                file_count=language_counts[language],
                total_bytes=language_bytes.get(language, 0),
            )

        return summary