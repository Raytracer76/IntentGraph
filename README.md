# IntentGraph 🧬

[![PyPI version](https://img.shields.io/pypi/v/intentgraph.svg)](https://pypi.org/project/intentgraph/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Static codebase analysis optimized for AI context windows** - Transform Python, JavaScript, and TypeScript codebases into structured, token-efficient intelligence that fits within AI agent token limits.

**✨ New in v0.4.0:** [RepoSnapshot v1](#-reposnapshot-v1-deterministic-snapshots) - Deterministic, version-controlled snapshots with runtime environment detection.

## 🎯 What IntentGraph Actually Does

IntentGraph is a **static code analysis CLI tool** that:

1. **Analyzes Python, JavaScript, and TypeScript codebases** using full AST parsing (with basic support for Go)
2. **Generates dependency graphs** with cycle detection and relationship tracking
3. **Calculates code metrics** (complexity, maintainability, LOC)
4. **Produces AI-optimized JSON output** in 3 levels (minimal ~10KB, medium ~70KB, full ~340KB)
5. **Intelligently clusters large repos** into navigable chunks that fit AI context windows
6. **Creates deterministic snapshots** with stable UUIDs and runtime environment detection (v0.4.0+)

### 🎪 What's Real vs. What's Framework

**✅ Fully Working:**
- Python, JavaScript, and TypeScript code analysis with full AST parsing
- Dependency graph generation with cycle detection
- Code complexity and maintainability metrics
- Three-level output system optimized for AI token limits
- Intelligent clustering for large codebases
- **RepoSnapshot v1: Deterministic snapshots with runtime detection** (v0.4.0+)
- CLI with comprehensive options
- Clean Architecture with excellent test coverage (143+ tests, 114 passing)

**🏗️ Framework/Scaffolding (Partial Implementation):**
- AI-native interface exists but query execution returns template data
- Natural language query parsing works, but semantic analysis is basic
- Agent context and response optimization structure is in place
- Task-aware optimization templates exist but need real implementation

**Bottom Line:** IntentGraph is a production-ready multi-language analysis tool (Python, JavaScript, TypeScript) with an AI-friendly output format, plus a well-architected framework for future AI-native capabilities.

## ⚡ The Problem IntentGraph Solves

**AI coding agents hit context limits.** A typical codebase can generate 1-2MB of raw analysis data. AI agents have ~200KB context windows.

**Solution:** IntentGraph pre-analyzes code and generates minimal, structured output that fits any AI context:
- **Minimal mode:** ~10KB per repository (paths, dependencies, basic metrics)
- **Medium mode:** ~70KB (+ key symbols, exports, quality scores)
- **Full mode:** ~340KB (complete analysis with all metadata)

For **massive codebases**, intelligent clustering breaks them into navigable 15KB chunks with an AI-friendly index.

## 🚀 Quick Start

### Installation
```bash
pip install intentgraph
```

### Basic Usage
```bash
# Analyze current directory (minimal output)
intentgraph .

# Generate cluster analysis for large repos
intentgraph . --cluster

# Full analysis with all metadata
intentgraph . --level full --output analysis.json

# Multi-language analysis
intentgraph /path/to/repo --lang py,js,ts
```

### Output Example
```json
{
  "files": [
    {
      "path": "src/analyzer.py",
      "language": "python",
      "dependencies": ["src/models.py", "src/utils.py"],
      "imports": ["pathlib", "typing", "ast"],
      "loc": 245,
      "complexity_score": 12
    }
  ],
  "language_summary": {
    "python": {
      "file_count": 42,
      "total_bytes": 125840
    }
  }
}
```

## 🔍 Core Features

### 1. Deep Multi-Language Analysis

**Python:**
- Full AST parsing for accurate symbol extraction
- Cyclomatic complexity calculation
- Maintainability index scoring
- Function-level dependencies tracking
- Public API detection (exports, `__all__`, underscore conventions)

**JavaScript:**
- Full AST parsing with tree-sitter
- ES6+ support (arrow functions, classes, template literals)
- CommonJS and ES module analysis
- Cyclomatic complexity calculation
- Import/export tracking

**TypeScript:**
- Full AST parsing with TypeScript-specific features
- Interface and type alias extraction
- Generic type parameter handling
- Decorator support
- Import/export analysis (including type imports)

### 2. Dependency Graph Generation
- **File-level dependencies** with import tracking
- **Cycle detection** and reporting
- **Graph statistics** (connected components, complexity)
- **NetworkX backend** for advanced graph operations

### 3. AI-Optimized Output Levels

**Minimal (~10KB):**
```json
{
  "path": "analyzer.py",
  "dependencies": ["models.py"],
  "imports": ["ast", "pathlib"],
  "loc": 245,
  "complexity_score": 12
}
```

**Medium (~70KB) adds:**
- Key symbols (classes, major functions)
- Export information
- Maintainability scores
- File purpose inference

**Full (~340KB) includes:**
- All symbols with signatures and docstrings
- Function-level dependencies
- Design patterns detected
- Complete metadata

### 4. Intelligent Clustering

For repos exceeding AI token limits even with minimal output:

```bash
intentgraph . --cluster --cluster-mode analysis --cluster-size 15KB
```

**Output Structure:**
```
.intentgraph/
├── index.json          # Navigation map with recommendations
├── domain.json         # Core business logic cluster
├── adapters.json       # External interfaces cluster
└── application.json    # Application services cluster
```

**Three Clustering Modes:**
- **analysis:** Dependency-based grouping (understand code structure)
- **refactoring:** Feature-based grouping (make targeted changes)
- **navigation:** Size-optimized grouping (explore large repos)

The **index.json** provides AI-friendly navigation:
```json
{
  "cluster_recommendations": {
    "understanding_codebase": ["domain", "application"],
    "finding_bugs": ["domain", "utilities"],
    "adding_features": ["application", "adapters"]
  },
  "clusters": [
    {
      "cluster_id": "domain",
      "file_count": 8,
      "total_size_kb": 12.4,
      "primary_concerns": ["data_models", "business_rules"],
      "complexity_score": 15
    }
  ]
}
```

## 🔒 RepoSnapshot v1: Deterministic Snapshots

**New in v0.4.0** - Version-controlled snapshots with deterministic UUIDs and runtime environment detection.

### Why RepoSnapshot?

Traditional IntentGraph analysis uses **random UUIDs** (different on each run), making it unsuitable for version control or change tracking. RepoSnapshot v1 solves this with:

- **Deterministic UUIDs**: SHA256-based, never change for the same file path
- **Stable Ordering**: All arrays sorted (files, imports, dependencies)
- **Cross-Platform**: Windows/Linux produce identical snapshots
- **Runtime Detection**: Package managers, tooling configs, version requirements
- **Schema Freeze**: v1.0.0 contract with semantic versioning guarantees

### Usage

```python
from pathlib import Path
from intentgraph.snapshot import RepoSnapshotBuilder

# Generate deterministic snapshot
builder = RepoSnapshotBuilder(Path.cwd())
snapshot = builder.build()

# Structure analysis
print(f"Files: {len(snapshot.structure.files)}")
print(f"Languages: {[lang.language for lang in snapshot.structure.languages]}")

# Runtime detection (no code execution!)
print(f"Package Manager: {snapshot.runtime.package_manager}")
print(f"Python Version: {snapshot.runtime.python_version}")
print(f"Tooling: {snapshot.runtime.tooling}")

# Serialize to JSON
json_output = builder.build_json(indent=2)
Path("snapshot.json").write_text(json_output)
```

### Schema Structure

```json
{
  "schema_version": "1.0.0",
  "snapshot_id": "7a44484a-15c4-4a42-ae2a-57bf42b931e7",
  "created_at": "2026-02-17T10:00:00Z",
  "structure": {
    "file_index": {
      "e0c8681a-5ec1-9106-384c-eaa1c315da83": "src/cli.py"
    },
    "files": [
      {
        "uuid": "e0c8681a-5ec1-9106-384c-eaa1c315da83",
        "path": "src/cli.py",
        "language": "python",
        "lines_of_code": 150,
        "complexity": 12,
        "imports": [...],
        "dependencies": [...]
      }
    ]
  },
  "runtime": {
    "package_manager": "pip",
    "python_version": ">=3.12",
    "tooling": {
      "pytest": "pyproject.toml",
      "ruff": "pyproject.toml",
      "mypy": "pyproject.toml"
    }
  }
}
```

### What's Detected

**Package Managers**: pnpm, npm, yarn, bun, pip, poetry, pipenv, conda
**Workspace Types**: pnpm-workspace, npm-workspaces, yarn-workspaces
**Tooling**: TypeScript, Vitest, Jest, ESLint, Prettier, pytest, ruff, mypy, black
**Versions**: Node.js (engines/nvmrc), Python (requires-python)

### Use Cases

- **Version Control**: Commit snapshots to track codebase evolution
- **Change Detection**: Compare snapshots to identify what changed
- **CI/CD Integration**: Generate snapshots before/after builds
- **AI Agent Context**: Stable, reproducible input for AI systems
- **Documentation**: Automatic runtime environment documentation

### Security

**Static Analysis Only** - No code execution, no network access, bounded file reads. Safe for untrusted codebases.

### Documentation

See **[docs/reposnapshot-v1.md](docs/reposnapshot-v1.md)** for complete documentation including:
- Full schema specification
- Configuration options (`include_tests`)
- Contract freeze details
- Determinism guarantees

### Examples

Real-world outputs from analyzing intentgraph itself: **[examples/snapshot_v1/](examples/snapshot_v1/)**

## 🤖 AI Integration Framework

IntentGraph includes a **framework** for AI-native interaction. The structure is in place, but semantic query execution is still evolving:

```python
from intentgraph import connect_to_codebase

# Framework exists for AI agent context
agent = connect_to_codebase("/path/to/repo", {
    "task": "bug_fixing",
    "token_budget": 30000
})

# Natural language query parsing works
results = agent.query("Find high complexity files")

# Returns structured response (currently template-based)
print(results["strategy"])  # Shows analysis strategy used
print(results["confidence"])  # Confidence level
```

**Current State:**
- ✅ Query parsing and intent detection
- ✅ Agent context management
- ✅ Token budget tracking
- ✅ Response optimization templates
- 🏗️ Semantic query execution (uses file-based filtering)
- 🏗️ Deep code understanding from natural language

**For Production:** Use the **CLI mode** for reliable analysis. The AI interface provides a foundation for future enhancements.

## 📊 Language Support

| Language   | Status | Features |
|------------|--------|----------|
| **Python** | ✅ Full | Complete AST parsing, complexity metrics, symbols, dependencies |
| **JavaScript** | ✅ Full | Full AST parsing, ES6+, complexity, imports/exports |
| **TypeScript** | ✅ Full | Full AST with TS features, interfaces, generics, decorators |
| Go | 🟡 Basic | File-level dependencies only |

**Enhanced analysis coming for:** Go, Rust, Java, C#

## ⚙️ Command Line Options

```bash
intentgraph [OPTIONS] REPOSITORY_PATH

Analysis Options:
  -o, --output FILE           Output file (- for stdout)
  --level [minimal|medium|full] Analysis detail level [default: minimal]
  --lang TEXT                 Languages to analyze (py,js,ts,go)
  --include-tests            Include test files in analysis
  --format [pretty|compact]  JSON output format
  --show-cycles              Print dependency cycles and exit with code 2
  --workers INTEGER          Parallel workers [default: CPU count]
  --debug                    Enable debug logging

Clustering Options:
  --cluster                  Enable cluster mode for large codebases
  --cluster-mode [analysis|refactoring|navigation]
                             Clustering strategy [default: analysis]
  --cluster-size [10KB|15KB|20KB]
                             Target cluster size [default: 15KB]
  --index-level [basic|rich] Index detail level [default: rich]
```

## 🏗️ Architecture

IntentGraph follows **Clean Architecture** principles:

```
┌─────────────────┐
│   CLI Layer     │  ← typer, rich console
├─────────────────┤
│ Application     │  ← Orchestration, services
├─────────────────┤
│   Domain        │  ← Core models, business logic
├─────────────────┤
│ Infrastructure  │  ← Parsers, git, I/O
└─────────────────┘
```

**Key Design Patterns:**
- Service-oriented application layer
- Dependency injection for testability
- Parser plugin architecture
- NetworkX for graph operations
- ProcessPoolExecutor for parallel analysis

## 🔧 Development

### Setup
```bash
git clone https://github.com/Raytracer76/intentgraph.git
cd intentgraph
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### Testing
```bash
pytest --cov=intentgraph --cov-report=term-missing
```

### Code Quality
```bash
ruff format .           # Format code
ruff check --fix .      # Lint and auto-fix
mypy .                  # Type checking
bandit -r src/          # Security scanning
```

## 📖 Use Cases

### 1. AI Agent Context Preparation
**Problem:** Large codebase won't fit in AI context window
**Solution:** Use minimal or clustered output

```bash
# Generate minimal analysis for AI agent
intentgraph /path/to/large-repo --level minimal --output ai-context.json

# For massive repos, use clustering
intentgraph /path/to/massive-repo --cluster --cluster-mode analysis
```

### 2. Code Quality Assessment
**Problem:** Need to identify technical debt and complexity hotspots
**Solution:** Use full analysis with metrics

```bash
intentgraph /path/to/repo --level full --output quality-report.json
```

### 3. Dependency Analysis
**Problem:** Need to understand module relationships and detect cycles
**Solution:** Check for dependency cycles

```bash
intentgraph /path/to/repo --show-cycles
```

### 4. Large Codebase Navigation
**Problem:** Repository too large for comprehensive analysis
**Solution:** Use clustering with navigation mode

```bash
intentgraph /path/to/large-repo --cluster --cluster-mode navigation
```

## 📈 Benchmarks

| Repository Size | Files | Analysis Time | Minimal Output | Full Output |
|----------------|-------|---------------|----------------|-------------|
| Small (< 50 files) | 42 | 2.3s | 8KB | 180KB |
| Medium (< 500 files) | 287 | 12.1s | 42KB | 2.1MB |
| Large (< 2000 files) | 1,654 | 45.7s | 156KB | 18.3MB |

*With clustering, large repos → 3-5 clusters of ~15KB each*

## 🎯 Why Choose IntentGraph

**vs GitHub Dependency Graph:**
- ✅ Function-level dependencies (not just file-level)
- ✅ Code quality metrics included
- ✅ AI-optimized output (3 levels)
- ✅ Intelligent clustering for large repos
- ✅ Offline analysis

**vs SonarQube:**
- ✅ AI-friendly JSON output
- ✅ Lightweight CLI tool
- ✅ Token-optimized for AI context windows
- ✅ No server infrastructure required
- ❌ Less comprehensive quality rules (trade-off for simplicity)

**vs Tree-sitter:**
- ✅ Higher-level semantic analysis (not just syntax)
- ✅ Dependency graph included
- ✅ Pre-optimized for AI consumption
- ✅ Built-in clustering for large repos
- ❌ Fewer languages supported (Python is priority)

## 🔮 Roadmap

**Near Term (v0.3.x):**
- Enhanced JavaScript/TypeScript analysis
- Incremental analysis support
- Performance optimizations
- More clustering strategies

**Medium Term (v0.4.x):**
- Real semantic query execution for AI interface
- Go and Rust language support
- Visual dependency graph generation
- VS Code extension

**Long Term (v1.0+):**
- Full AI-native autonomous capabilities
- Multi-language unified analysis
- ML-based pattern detection
- Cloud-hosted analysis API

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Adding Language Support
1. Create parser in `src/intentgraph/adapters/parsers/`
2. Implement `extract_code_structure()` method
3. Add tests and examples
4. Submit PR with documentation

### Ideas for Contributions
- **Enhanced JavaScript/TypeScript parser** with full AST analysis
- **Go/Rust language support**
- **Performance optimizations** for large repos
- **Incremental analysis** (only analyze changed files)
- **Visual dependency graphs** (SVG/PNG generation)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI
- Uses [grimp](https://github.com/seddonym/grimp) for Python dependency analysis
- Powered by Python's [ast](https://docs.python.org/3/library/ast.html) module
- Graph operations via [NetworkX](https://networkx.org/)
- Code quality enforcement with [Ruff](https://github.com/astral-sh/ruff)

## 📞 Support

- **GitHub Issues** - Bug reports and feature requests
- **Discussions** - Questions and community chat
- **Documentation** - See `/docs` directory for detailed guides

---

**Made for the AI coding agent era** 🤖

IntentGraph helps AI agents understand codebases by providing pre-analyzed, structured intelligence that fits within their context limits. It's a production-ready analysis tool with a vision for autonomous AI integration.
