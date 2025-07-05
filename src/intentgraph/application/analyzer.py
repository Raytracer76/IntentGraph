"""Repository analysis orchestration."""

import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
from pathlib import Path

from ..adapters.git import GitIgnoreHandler
from ..adapters.parsers import get_parser_for_language
from ..domain.exceptions import InvalidRepositoryError
from ..domain.graph import DependencyGraph
from ..domain.models import AnalysisResult, FileInfo, Language, LanguageSummary

logger = logging.getLogger(__name__)


class RepositoryAnalyzer:
    """Orchestrates repository analysis."""

    def __init__(
        self,
        workers: int | None = None,
        include_tests: bool = False,
        language_filter: list[Language] | None = None,
    ) -> None:
        self.workers = workers or cpu_count()
        self.include_tests = include_tests
        self.language_filter = set(language_filter) if language_filter else None
        self.graph = DependencyGraph()
        self._git_handler = GitIgnoreHandler()

    def analyze(self, repo_path: Path) -> AnalysisResult:
        """Analyze a repository and return results."""
        if not repo_path.exists():
            raise InvalidRepositoryError(f"Repository path does not exist: {repo_path}")

        if not (repo_path / ".git").exists():
            raise InvalidRepositoryError(f"Path is not a Git repository: {repo_path}")

        logger.info(f"Analyzing repository: {repo_path}")

        # Initialize git ignore handler
        self._git_handler.load_gitignore(repo_path)

        # Find all source files
        source_files = self._find_source_files(repo_path)
        logger.info(f"Found {len(source_files)} source files")

        # Analyze files in parallel
        file_infos = self._analyze_files(source_files, repo_path)

        # Build dependency graph
        self._build_dependency_graph(file_infos, repo_path)

        # Generate summary
        language_summary = self._generate_language_summary(file_infos, source_files)

        return AnalysisResult(
            root=repo_path,
            language_summary=language_summary,
            files=file_infos,
        )

    def _find_source_files(self, repo_path: Path) -> list[Path]:
        """Find all source files in the repository."""
        source_files = []

        for file_path in repo_path.rglob("*"):
            try:
                if not file_path.is_file():
                    continue
            except (OSError, PermissionError):
                # Skip files that can't be accessed (e.g., broken symlinks, permission issues)
                continue

            # Skip if ignored by git
            if self._git_handler.is_ignored(file_path, repo_path):
                continue

            # Skip test files if not included
            if not self.include_tests and self._is_test_file(file_path):
                continue

            # Check language filter
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

    def _analyze_files(self, source_files: list[Path], repo_path: Path) -> list[FileInfo]:
        """Analyze files to extract metadata."""
        file_infos = []

        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self._analyze_single_file, file_path, repo_path): file_path
                for file_path in source_files
            }

            # Collect results
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_info = future.result()
                    if file_info:
                        file_infos.append(file_info)
                        self.graph.add_file(file_info)
                except Exception as e:
                    logger.warning(f"Failed to analyze {file_path}: {e}")

        return file_infos

    @staticmethod
    def _analyze_single_file(file_path: Path, repo_path: Path) -> FileInfo | None:
        """Analyze a single file with enhanced structure analysis."""
        try:
            # Start with basic file info
            basic_info = FileInfo.from_path(file_path, repo_path)
            
            # Get enhanced parser for detailed analysis
            from ..adapters.parsers.enhanced_python_parser import EnhancedPythonParser
            from ..domain.models import Language
            
            if basic_info.language == Language.PYTHON:
                parser = EnhancedPythonParser()
                
                # Extract detailed code structure
                symbols, exports, func_deps, imports, metadata = parser.extract_code_structure(
                    file_path, repo_path
                )
                
                # Infer file purpose from symbols and path
                file_purpose = RepositoryAnalyzer._infer_file_purpose(basic_info.path, symbols)
                key_abstractions = RepositoryAnalyzer._extract_key_abstractions(symbols)
                design_patterns = RepositoryAnalyzer._detect_design_patterns(symbols, exports)
                
                # Create enhanced FileInfo
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
            else:
                # For non-Python files, return basic info for now
                return basic_info
                
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")
            return None

    def _build_dependency_graph(self, file_infos: list[FileInfo], repo_path: Path) -> None:
        """Build dependency graph between files."""
        # Create mapping from path to file info
        path_to_file = {str(f.path): f for f in file_infos}

        for file_info in file_infos:
            parser = get_parser_for_language(file_info.language)
            if not parser:
                continue

            try:
                full_path = repo_path / file_info.path
                dependencies = parser.extract_dependencies(full_path, repo_path)

                # Convert paths to file IDs
                dependency_ids = []
                for dep_path in dependencies:
                    if dep_path in path_to_file:
                        dependency_ids.append(path_to_file[dep_path].id)
                        self.graph.add_dependency(file_info.id, path_to_file[dep_path].id)

                # Update file info with dependencies
                file_info.dependencies.extend(dependency_ids)

            except Exception as e:
                logger.warning(f"Failed to extract dependencies for {file_info.path}: {e}")

    def _generate_language_summary(
        self, file_infos: list[FileInfo], source_files: list[Path]
    ) -> dict[Language, LanguageSummary]:
        """Generate language summary statistics."""
        summary = {}

        # Count files by language
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

        # Create summaries
        for language in language_counts:
            summary[language] = LanguageSummary(
                file_count=language_counts[language],
                total_bytes=language_bytes.get(language, 0),
            )

        return summary
    
    @staticmethod
    def _infer_file_purpose(file_path: Path, symbols: list) -> str:
        """Infer the purpose of a file from its path and symbols."""
        path_str = str(file_path).lower()
        
        # Path-based inference
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
        
        # Symbol-based inference
        from ..domain.models import CodeSymbol
        
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
    
    @staticmethod
    def _extract_key_abstractions(symbols: list) -> list[str]:
        """Extract key abstractions (main classes/concepts) from symbols."""
        from ..domain.models import CodeSymbol
        
        abstractions = []
        
        for symbol in symbols:
            if symbol.symbol_type == "class" and symbol.is_exported:
                abstractions.append(symbol.name)
            elif symbol.symbol_type in ("function", "async_function") and symbol.is_exported:
                # Only include if it's a significant function (has docstring or is decorated)
                if symbol.docstring or symbol.decorators:
                    abstractions.append(symbol.name)
                    
        return abstractions[:5]  # Limit to top 5 key abstractions
    
    @staticmethod
    def _detect_design_patterns(symbols: list, exports: list) -> list[str]:
        """Detect common design patterns in the code."""
        from ..domain.models import CodeSymbol
        
        patterns = []
        
        # Check for common patterns based on symbols
        class_names = [s.name for s in symbols if s.symbol_type == "class"]
        
        # Factory pattern
        if any("Factory" in name for name in class_names):
            patterns.append("factory")
            
        # Singleton pattern (check for decorators or __new__ method)
        for symbol in symbols:
            if "singleton" in str(symbol.decorators).lower():
                patterns.append("singleton")
                break
                
        # Parser pattern
        if any("Parser" in name for name in class_names):
            patterns.append("parser")
            
        # Adapter pattern
        if any("Adapter" in name for name in class_names):
            patterns.append("adapter")
            
        # Builder pattern
        if any("Builder" in name for name in class_names):
            patterns.append("builder")
            
        # Observer pattern
        if any("Observer" in name or "Listener" in name for name in class_names):
            patterns.append("observer")
            
        # Command pattern
        if any("Command" in name for name in class_names):
            patterns.append("command")
            
        # Strategy pattern
        if any("Strategy" in name for name in class_names):
            patterns.append("strategy")
            
        return patterns
