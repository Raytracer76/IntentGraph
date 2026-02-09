# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**IntentGraph** is a static code analysis CLI tool optimized for AI agent context windows. It analyzes Python, JavaScript, and TypeScript codebases (with basic Go support) and generates token-efficient structured output that fits within AI agent limitations.

**Version**: 0.3.0-dev
**Python**: 3.12+
**License**: MIT

## Core Purpose

IntentGraph solves the **context window problem** for AI coding agents by:
- Pre-analyzing Python, JavaScript, and TypeScript codebases into minimal, AI-optimized output (~10KB vs 340KB full analysis)
- Providing function-level dependency tracking and code metrics (complexity, maintainability)
- Offering intelligent clustering for massive repositories that exceed token limits
- Exposing a production-ready CLI with an AI integration framework for future expansion

## What's Real vs. What's Framework

**✅ Fully Working:**
- Python, JavaScript, and TypeScript code analysis with complete AST parsing
- Dependency graph generation with cycle detection
- Code complexity and maintainability metrics
- Three-level output system (minimal, medium, full)
- Intelligent clustering for large codebases
- Comprehensive CLI with rich options
- 617+ tests (Python: pytest, JavaScript: 301 tests, TypeScript: 316 tests)

**🏗️ Framework/Scaffolding:**
- AI-native interface exists with structure in place
- Natural language query parsing works
- Semantic query execution uses basic file filtering (not deep AI understanding)
- Response optimization returns template data
- Task-aware optimization structure exists but needs full implementation

## Quick Commands

### Development Setup
```bash
# Clone and setup
git clone <repo-url>
cd intentgraph
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests with coverage
pytest --cov=intentgraph --cov-report=term-missing

# Run specific test file
pytest tests/test_domain/test_models.py -v

# Run tests excluding slow tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration

# Run with specific coverage threshold
pytest --cov=intentgraph --cov-fail-under=90
```

### Code Quality
```bash
# Format code (ALWAYS run before committing)
ruff format .

# Lint and auto-fix
ruff check --fix .

# Type checking
mypy .

# Security scanning
bandit -r src/

# Run all quality checks
ruff format . && ruff check --fix . && mypy . && bandit -r src/
```

### CLI Usage (Primary Interface)
```bash
# Analyze current directory (minimal output, AI-friendly)
intentgraph .

# Generate cluster analysis for large codebases
intentgraph . --cluster --cluster-mode analysis

# Full analysis with all metadata
intentgraph . --level full --output analysis.json

# Multi-language analysis (Python, JavaScript, TypeScript)
intentgraph /path/to/repo --lang py,js,ts

# Check for circular dependencies
intentgraph . --show-cycles
```

### Programmatic Usage
```bash
# Traditional Python API (production-ready)
from intentgraph import RepositoryAnalyzer
analyzer = RepositoryAnalyzer(workers=4, include_tests=False)
result = analyzer.analyze(Path("/path/to/repo"))

# AI Integration Framework (experimental)
from intentgraph import connect_to_codebase
agent = connect_to_codebase("/path/to/repo", {"task": "bug_fixing"})
results = agent.query("Find high complexity files")
# Note: Query execution uses file-based filtering, not deep semantic analysis
```

## Architecture Overview

IntentGraph follows **Clean Architecture** principles with strict layer separation:

```
┌─────────────────┐
│   CLI Layer     │  ← typer, rich console (intentgraph.cli)
├─────────────────┤
│ Application     │  ← Orchestration, services (intentgraph.application)
├─────────────────┤
│   Domain        │  ← Core models, business logic (intentgraph.domain)
├─────────────────┤
│ Infrastructure  │  ← Parsers, git, I/O (intentgraph.adapters)
└─────────────────┘
```

### Layer Responsibilities

**CLI Layer (`src/intentgraph/cli.py`)**:
- Command-line interface with typer
- Rich console output and progress bars
- Validates user input (languages, paths, parameters)
- Orchestrates high-level operations

**Application Layer (`src/intentgraph/application/`)**:
- `analyzer.py`: Main `RepositoryAnalyzer` orchestrator
- `services.py`: Focused services (FileDiscovery, CodeAnalysis, DependencyGraph, LanguageSummary)
- `clustering.py`: `ClusteringEngine` for large codebase navigation
- `streaming_analyzer.py`: Memory-efficient streaming analysis

**Domain Layer (`src/intentgraph/domain/`)**:
- `models.py`: Core entities (`FileInfo`, `CodeSymbol`, `AnalysisResult`, `Language`)
- `graph.py`: `DependencyGraph` with cycle detection (NetworkX)
- `clustering.py`: Clustering domain models (`ClusterConfig`, `ClusterMode`)
- `exceptions.py`: Domain-specific exceptions

**Infrastructure Layer (`src/intentgraph/adapters/`)**:
- `parsers/`: Language-specific parsers (Python enhanced, JS/TS/Go basic)
- `git.py`: GitIgnore handling with pathspec
- `file_repository.py`: File system abstraction
- `output.py`: JSON serialization with orjson

### AI Integration Framework (`src/intentgraph/ai/`)

Framework for AI-native interaction (partial implementation):
- `agent.py`: `CodebaseAgent` class with agent context management
- `manifest.py`: Static capabilities manifest
- `query.py`: Natural language query parsing (intent detection)
- `navigation.py`: Navigation strategies with file filtering
- `response.py`: Response template system

**Current Implementation:**
- ✅ **Query Parsing**: Natural language intent detection works
- ✅ **Agent Context**: Task-based context management implemented
- ✅ **Token Budget**: Budget tracking and tier management
- ✅ **Response Templates**: Structured response formatting
- 🏗️ **Semantic Execution**: Uses file-based filtering, not deep AI understanding
- 🏗️ **Autonomous Navigation**: Strategy selection works, execution is basic

**For Production Use:**
- Use the **CLI** (`intentgraph` command) for reliable analysis
- Use `RepositoryAnalyzer` class for programmatic access
- AI framework provides structure for future enhancements

## Key Design Patterns

### 1. Parser Plugin Architecture

Each language has a parser implementing `LanguageParser` interface:
- **Base**: `src/intentgraph/adapters/parsers/base.py` - Abstract `LanguageParser` class
- **Python**: `enhanced_python_parser.py` - Full AST analysis with complexity metrics
- **JavaScript/TypeScript/Go**: Basic parsers with file-level dependencies only

**Adding a New Language**:
1. Create `src/intentgraph/adapters/parsers/your_language_parser.py`
2. Implement `extract_code_structure(code: str, file_path: Path) -> FileInfo`
3. Register in `parsers/__init__.py` `get_parser_for_language()` function
4. Add to `Language` enum in `domain/models.py`
5. Write tests in `tests/test_adapters/test_your_language_parser.py`

### 2. Service-Oriented Application Layer

The `RepositoryAnalyzer` delegates to focused services:
- `FileDiscoveryService`: Find source files, apply .gitignore
- `CodeAnalysisService`: Parse files in parallel with ProcessPoolExecutor
- `DependencyGraphService`: Build NetworkX graph, detect cycles
- `LanguageSummaryService`: Aggregate statistics per language

**Why**: Separation of concerns, easier testing, clear responsibilities.

### 3. Dependency Injection

`RepositoryAnalyzer` accepts:
- `parser_factory: ParserFactory` - for custom parser implementations
- `file_repository: FileRepository` - for testing without filesystem

**Testing Pattern**:
```python
# Use mock file repository for tests
mock_repo = MockFileRepository(test_files)
analyzer = RepositoryAnalyzer(file_repository=mock_repo)
```

### 4. Three-Level Output System

**Minimal** (~10KB): Paths, dependencies, imports, basic metrics - DEFAULT, AI-friendly
**Medium** (~70KB): + Key symbols, exports, maintainability scores
**Full** (~340KB): Complete analysis with all metadata

Implementation: `cli.py:filter_result_by_level()` post-processes `AnalysisResult`

**Why**: AI agents have token limits (~200KB). Minimal output ensures entire codebase fits in context.

### 5. Intelligent Clustering

For massive repositories exceeding AI context limits even with minimal output:

**Three Clustering Modes**:
- **`analysis`**: Dependency-based grouping (code understanding)
- **refactoring**: Feature-based grouping (targeted changes)
- **navigation**: Size-optimized grouping (exploration)

**Output Structure**:
```
.intentgraph/              # Default output directory
├── index.json            # AI navigation map with recommendations
├── domain.json           # Core business logic cluster
├── adapters.json         # External interfaces cluster
└── application.json      # Application services cluster
```

**Key Feature**: `index.json` provides AI agents with:
- Cluster recommendations per task (`"finding_bugs": ["domain", "utilities"]`)
- Cross-cluster dependencies
- File-to-cluster mapping
- Cluster metadata (complexity, primary concerns)

## Important Implementation Details

### 1. Parallel Analysis

`CodeAnalysisService` uses `ProcessPoolExecutor` for multi-core analysis:
```python
with ProcessPoolExecutor(max_workers=self.workers) as executor:
    futures = {executor.submit(self._analyze_file, file_path): file_path
               for file_path in source_files}
```

**Why ProcessPoolExecutor**: AST parsing is CPU-bound, not I/O-bound. Processes avoid GIL.

### 2. Python Enhanced Parser

`enhanced_python_parser.py` provides deep analysis:
- AST traversal for symbols (functions, classes, variables)
- Cyclomatic complexity calculation
- Maintainability index (volume, complexity, lines)
- Decorator detection
- Public API detection (`__all__`, leading underscore rules)
- Function-level dependency tracking

**Complexity Calculation**: Based on control flow nodes (if, for, while, and, or, etc.)

### 3. Dependency Graph

Uses NetworkX for graph operations:
- `add_file()`: Nodes are file paths
- `add_dependency()`: Directed edges from file to imported file
- `has_cycles()`: Uses NetworkX cycle detection
- `get_cycles()`: Returns list of cycle paths

**Critical**: Cycles indicate potential circular dependency issues.

### 4. .gitignore Handling

`git.py` adapter uses `pathspec` library:
- Reads `.gitignore` recursively
- Applies patterns with Git semantics
- Respects negation patterns (`!important.py`)

**ALWAYS exclude**: `.git/`, `.intentgraph/`, virtual environments, `__pycache__/`, etc.

### 5. Validation and Security

**CLI Input Validation**:
- `validate_languages_input()`: Unicode normalization, character whitelist, length limits
- Path validation: Must exist, must be git repository
- Language codes: Only allow known languages (py, js, ts, go)

**No Code Execution**: Static analysis only via AST parsing, never use dynamic code execution.

## Testing Strategy

**Test Structure**:
```
tests/
├── conftest.py                    # pytest fixtures
├── test_cli.py                    # CLI integration tests
├── test_adapters/                 # Infrastructure layer tests
├── test_application/              # Application layer tests
├── test_domain/                   # Domain layer tests
├── integration/                   # End-to-end tests
├── performance/                   # Benchmark tests
└── property_based/                # Hypothesis tests
```

**Coverage Requirements**: 90% minimum (enforced in pyproject.toml)

**Test Patterns**:
```python
# Use fixtures for test repositories
def test_analysis(temp_repo):
    analyzer = RepositoryAnalyzer()
    result = analyzer.analyze(temp_repo)
    assert len(result.files) > 0

# Use property-based testing for parsers
@given(st.text())
def test_parser_never_crashes(code):
    parser.extract_code_structure(code, Path("test.py"))
```

## Configuration Files

**pyproject.toml**: Central configuration
- Build system: hatchling
- Dependencies and optional dev dependencies
- pytest configuration (markers, coverage thresholds)
- mypy strict type checking configuration
- ruff linting rules (select, ignore)
- bandit security scanning exclusions

**Key Settings**:
- `requires-python = ">=3.12"` - Modern Python required
- `--cov-fail-under=90` - 90% coverage enforced
- `strict = true` (mypy) - Strict type checking
- `target-version = "py312"` (ruff) - Modern Python syntax

## Dependencies

**Core Runtime**:
- `typer` + `rich`: CLI framework and output
- `pydantic`: Data validation and serialization
- `grimp`: Python import graph analysis
- `tree-sitter-language-pack`: Multi-language parsing
- `networkx`: Graph algorithms and cycle detection
- `orjson`: Fast JSON serialization

**Development**:
- `pytest` + `pytest-cov` + `pytest-asyncio`: Testing
- `hypothesis`: Property-based testing
- `mypy`: Type checking
- `ruff`: Fast linting and formatting (replaces black, isort, flake8)
- `bandit`: Security vulnerability detection

## Common Development Workflows

### Adding a New Feature

1. **Write tests first** (TDD):
```bash
# Create test file
touch tests/test_new_feature.py
# Write failing tests
pytest tests/test_new_feature.py  # Should fail
```

2. **Implement feature** in appropriate layer:
```bash
# Domain layer for business logic
vim src/intentgraph/domain/new_feature.py
# Application layer for orchestration
vim src/intentgraph/application/new_feature_service.py
```

3. **Run tests and quality checks**:
```bash
pytest tests/test_new_feature.py
ruff format . && ruff check --fix . && mypy .
```

4. **Update documentation** if needed (README.md, docs/)

### Adding Language Support

1. **Create parser** implementing `LanguageParser`:
```python
# src/intentgraph/adapters/parsers/rust_parser.py
class RustParser(LanguageParser):
    def extract_code_structure(self, code: str, file_path: Path) -> FileInfo:
        # Implement Rust parsing logic
        pass
```

2. **Register in factory**:
```python
# src/intentgraph/adapters/parsers/__init__.py
def get_parser_for_language(language: Language) -> LanguageParser | None:
    if language == Language.RUST:
        return RustParser()
```

3. **Add to Language enum**:
```python
# src/intentgraph/domain/models.py
class Language(str, Enum):
    RUST = "rust"
    # Update from_extension()
```

4. **Write comprehensive tests**:
```python
# tests/test_adapters/test_rust_parser.py
def test_rust_parser_extracts_functions():
    parser = RustParser()
    result = parser.extract_code_structure(rust_code, Path("test.rs"))
    assert len(result.symbols) > 0
```

### Debugging Analysis Issues

**Enable debug logging**:
```bash
intentgraph /path/to/repo --debug
```

**Check specific file parsing**:
```python
from intentgraph.adapters.parsers import get_parser_for_language
from intentgraph.domain.models import Language
from pathlib import Path

parser = get_parser_for_language(Language.PYTHON)
result = parser.extract_code_structure(code, Path("test.py"))
print(result)
```

**Inspect dependency graph**:
```python
analyzer = RepositoryAnalyzer()
result = analyzer.analyze(Path("/path/to/repo"))
graph = analyzer.graph

# Check for cycles
if graph.has_cycles():
    cycles = graph.get_cycles()
    print(f"Found {len(cycles)} cycles")
```

## Entry Points

**CLI**: `src/intentgraph/cli.py:main()` (registered as `intentgraph` command)

**Programmatic**:
```python
# Traditional interface
from intentgraph import RepositoryAnalyzer
analyzer = RepositoryAnalyzer(workers=4, include_tests=False)
result = analyzer.analyze(Path("/path/to/repo"))

# AI-native interface
from intentgraph import connect_to_codebase
agent = connect_to_codebase("/path/to/repo", {"task": "bug_fixing"})
results = agent.query("Find high complexity files")
```

## Important Notes

### Git Operations
- Repository MUST be a git repository (`.git/` directory required)
- `.gitignore` patterns are automatically respected
- `.intentgraph/` output directory should be gitignored (add to `.gitignore`)

### Performance Considerations
- Parallel analysis scales with CPU cores (default: `cpu_count()`)
- Large repositories: Use `--cluster` to avoid memory issues
- Streaming analyzer available for very large repos: `StreamingAnalyzer`

### Type Safety
- **Strict mypy enforcement**: All code must pass `mypy .` with strict mode
- Use explicit types, no `Any` unless absolutely necessary
- Pydantic models for data validation at boundaries

### Code Style
- **Line length**: 88 characters (Black-compatible)
- **Imports**: Organized by ruff (stdlib, third-party, local)
- **Strings**: Double quotes (enforced by ruff)
- **Type annotations**: Required for all functions (mypy strict)

### Security
- **Input validation**: All user inputs validated and sanitized
- **No code execution**: Static analysis only, never use dynamic code execution
- **Path traversal**: Paths validated to prevent escaping repository
- **Bandit scanning**: Run before committing

## AI-Native Interface Special Considerations

When modifying AI-native interface (`src/intentgraph/ai/`):

1. **Maintain Backward Compatibility**: Autonomous agents depend on stable manifest schema
2. **Update Capabilities Manifest**: `manifest.py` must reflect all agent capabilities
3. **Token Budget Awareness**: Responses must respect agent token budgets
4. **Task-Specific Optimization**: Different agent tasks need different response formats
5. **Self-Describing**: Interface should be discoverable without human documentation

**Critical Files**:
- `ai/manifest.py`: Capabilities manifest for autonomous discovery
- `ai/agent.py`: `CodebaseAgent` class with natural language query interface
- `ai/query.py`: Natural language query parser and executor
- `ai/navigation.py`: Intelligent navigation recommendations
- `ai/response.py`: Task-aware, token-optimized response formatter

## Error Handling Philosophy

- **Fail early**: Validate inputs at CLI layer, raise clear exceptions
- **Graceful degradation**: If one file fails to parse, log and continue
- **Rich error messages**: Use `rich.console` for user-friendly errors
- **Custom exceptions**: Domain exceptions in `domain/exceptions.py`

**Exception Hierarchy**:
- `IntentGraphError` (base)
  - `InvalidRepositoryError`
  - `ParsingError`
  - `CyclicDependencyError`
  - `UnsupportedLanguageError`

## Documentation Structure

- **README.md**: User-facing documentation, features, quick start
- **docs/architecture.md**: Deep dive into Clean Architecture layers
- **docs/agent_workflows.md**: AI agent integration patterns and workflows
- **docs/language_support.md**: Language parser capabilities and status
- **examples/**: Runnable example scripts
  - `ai_native/`: AI-native interface demos
  - `clustering/`: Clustering mode comparisons
  - `basic_usage/`: Simple programmatic examples

## Version and Release Process

**Version**: Defined in `src/intentgraph/__init__.py:__version__`

**Current**: `0.3.0-dev` (development version)

**Versioning**: Semantic versioning (MAJOR.MINOR.PATCH)
- MAJOR: Breaking changes to public API or AI-native interface
- MINOR: New features, backward-compatible
- PATCH: Bug fixes, backward-compatible

**Before Release**:
1. Update version in `__init__.py`
2. Update CHANGELOG.md with release notes
3. Run full test suite: `pytest --cov=intentgraph --cov-fail-under=90`
4. Run quality checks: `ruff format . && ruff check . && mypy . && bandit -r src/`
5. Build and test package: `python -m build && pip install dist/*.whl`

## Contributing Guidelines

See CONTRIBUTING.md for full details. Key points:
- Python 3.12+ required
- Run `ruff format .` before committing (enforced)
- Maintain 90% test coverage (enforced)
- Pass mypy strict type checking (enforced)
- Write tests for new features (TDD encouraged)
- Update documentation for user-facing changes

---

**Last Updated**: 2026-02-09
**IntentGraph Version**: 0.3.0-dev
