# RepoSnapshot v1 Documentation

**Version**: 1.0.0
**Status**: Stable
**Module**: `intentgraph.snapshot`

## Overview

RepoSnapshot v1 combines IntentGraph's code structure analysis with runtime environment detection into a single, deterministic JSON artifact. It captures **what code exists** (structure) and **how it runs** (runtime configuration) in a reproducible format suitable for version control, change tracking, and AI agent context.

**What it actually does**:
- Analyzes Python, JavaScript, and TypeScript files (basic Go support)
- Extracts file metadata, imports, dependencies, and code symbols
- Detects package managers, workspace types, and tooling configurations
- Generates deterministic UUIDs for files based on path hashing
- Produces stable, sorted JSON output (~30KB typical size)

**What it does NOT do**:
- Does not execute code or shell commands
- Does not make network requests
- Does not analyze binary files or large media
- Does not perform deep semantic analysis (uses AST parsing only)

## Security Note

**Static Analysis Only**: RepoSnapshot performs read-only static analysis with no code execution, no network access, and bounded file reads. It parses source files via AST, reads configuration files as plain text, and never invokes interpreters, compilers, or package managers. Safe for untrusted codebases.

## Schema Specification

### Top-Level Structure

```json
{
  "schema_version": "1.0.0",
  "snapshot_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-02-17T12:34:56.789Z",
  "structure": { /* StructureSnapshot */ },
  "runtime": { /* RuntimeSnapshot */ }
}
```

**Fields**:
- `schema_version` (string): Semantic version of schema (frozen at "1.0.0")
- `snapshot_id` (string): UUID v4 identifier for this snapshot instance
- `created_at` (string): ISO 8601 timestamp (UTC)
- `structure` (object): Code structure analysis (files, languages, dependencies)
- `runtime` (object): Runtime environment detection (package manager, tooling, scripts)

### StructureSnapshot

```json
{
  "root_path": "/absolute/path/to/repo",
  "analyzed_at": "2026-02-17T12:34:56.789Z",
  "languages": [
    {
      "language": "python",
      "file_count": 42,
      "total_bytes": 123456
    }
  ],
  "file_index": {
    "550e8400-e29b-41d4-a716-446655440000": "src/main.py",
    "6ba7b810-9dad-11d1-80b4-00c04fd430c8": "src/utils.py"
  },
  "files": [
    {
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "path": "src/main.py",
      "language": "python",
      "lines_of_code": 150,
      "complexity": 12,
      "imports": ["os", "sys", "./utils"],
      "dependencies": ["6ba7b810-9dad-11d1-80b4-00c04fd430c8"]
    }
  ]
}
```

**Fields**:
- `root_path` (string): Absolute repository root path (POSIX-style forward slashes)
- `analyzed_at` (string): ISO 8601 timestamp of structure analysis
- `languages` (array): Language statistics, **sorted by language name**
  - `language` (string): Language identifier (python, javascript, typescript, go)
  - `file_count` (integer): Number of files in this language
  - `total_bytes` (integer): Sum of file sizes in bytes
- `file_index` (object): UUID → relative path mapping, **sorted by UUID**
- `files` (array): File metadata entries, **sorted by path**
  - `uuid` (string): Deterministic UUID generated from file path
  - `path` (string): Relative file path from repository root (POSIX-style)
  - `language` (string): Detected language
  - `lines_of_code` (integer): Non-comment, non-blank lines
  - `complexity` (integer): Cyclomatic complexity score (Python only, 0 for others)
  - `imports` (array): Import statements, **sorted alphabetically**
  - `dependencies` (array): UUIDs of files this file imports, **sorted**

### RuntimeSnapshot

```json
{
  "package_manager": "pnpm",
  "workspace_type": "pnpm-workspace",
  "node_version": "20.10.0",
  "python_version": "3.12",
  "tooling": {
    "typescript": "tsconfig.json",
    "vitest": "vitest.config.ts",
    "eslint": ".eslintrc.json",
    "prettier": ".prettierrc",
    "pytest": "pyproject.toml",
    "ruff": "pyproject.toml",
    "mypy": "mypy.ini",
    "black": "pyproject.toml"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "test": "vitest"
  }
}
```

**Fields**:
- `package_manager` (string | null): Detected package manager
  - Values: `pnpm`, `npm`, `yarn`, `bun`, `pip`, `poetry`, `pipenv`, `conda`, `unknown`, `null`
  - Detection priority: pnpm-lock.yaml → package-lock.json → yarn.lock → poetry.lock → etc.
- `workspace_type` (string | null): Workspace configuration type
  - Values: `pnpm-workspace`, `npm-workspaces`, `yarn-workspaces`, `null`
- `node_version` (string | null): Node.js version from package.json engines or .nvmrc
- `python_version` (string | null): Python version from pyproject.toml `requires-python`
- `tooling` (object): Configuration file paths for detected tools (all fields optional)
  - TypeScript: `typescript` (tsconfig.json location)
  - Testing: `vitest`, `jest`, `pytest`
  - Linting: `eslint`, `ruff`, `mypy`
  - Formatting: `prettier`, `black`
- `scripts` (object): Extracted npm/pnpm scripts or pyproject.toml scripts

**Tooling Detection Rules**:
- Precedence: Dedicated config files take priority over pyproject.toml sections
  - Example: `mypy.ini` overrides `[tool.mypy]` in pyproject.toml
- Discovery: Searches repository root and common config directories
- No execution: Reads files as text, does not validate syntax

## Usage

### Programmatic API

```python
from pathlib import Path
from intentgraph.snapshot import RepoSnapshotBuilder

# Basic usage
builder = RepoSnapshotBuilder(Path("/path/to/repo"))
snapshot = builder.build()

# Access structure data
print(f"Files analyzed: {len(snapshot.structure.files)}")
print(f"Languages: {[lang.language for lang in snapshot.structure.languages]}")

# Access runtime data
print(f"Package manager: {snapshot.runtime.package_manager}")
print(f"Scripts: {snapshot.runtime.scripts}")

# Serialize to JSON
json_output = builder.build_json(indent=2)
Path("snapshot.json").write_text(json_output)
```

### Configuration Options

```python
from intentgraph import RepositoryAnalyzer
from intentgraph.snapshot import RepoSnapshotBuilder

# Custom analyzer with test file inclusion
analyzer = RepositoryAnalyzer(
    include_tests=True,      # Include test files in analysis
    workers=8,               # Parallel analysis workers (default: cpu_count())
    language_filter=None     # Filter to specific languages (default: all)
)

# Use custom analyzer
builder = RepoSnapshotBuilder(repo_path)
snapshot = builder.build(analysis_result=analyzer.analyze(repo_path))
```

#### `include_tests` Configuration

**Default**: `False` (test files excluded)

The `include_tests` parameter controls whether files identified as test files are included in structure analysis. This is a **consumer choice**, not a hidden heuristic.

**Test File Detection**:
Files are classified as "test files" if they match ANY of:
- Path contains "test" or "spec" (case-insensitive)
- Filename starts with `test_` (Python convention)
- Filename ends with `_test.py`, `.test.js`, `.test.ts`, `.spec.js`, `.spec.ts`

**When to use `include_tests=True`**:
- Analyzing test fixture repositories (files in `tests/` directories that aren't actual tests)
- Full codebase analysis including test coverage
- Understanding test structure and dependencies

**When to use `include_tests=False` (default)**:
- Production code analysis only
- Minimizing snapshot size
- Focusing on application logic without test overhead

**Example**:
```python
# Exclude tests (default) - production code only
builder = RepoSnapshotBuilder(repo_path)
snapshot = builder.build()  # Test files filtered out

# Include tests - full codebase analysis
from intentgraph import RepositoryAnalyzer
analyzer = RepositoryAnalyzer(include_tests=True)
snapshot = builder.build(analysis_result=analyzer.analyze(repo_path))
```

### CLI Usage (Future)

**Note**: CLI integration for snapshots is planned but not yet implemented. Current CLI (`intentgraph`) generates `AnalysisResult` format, not `RepoSnapshot` format.

Planned:
```bash
# Generate snapshot (planned)
intentgraph snapshot . --output snapshot.json

# Include test files (planned)
intentgraph snapshot . --include-tests --output snapshot.json
```

## Determinism Guarantees

RepoSnapshot v1 guarantees **byte-identical output** for identical repository state (excluding timestamps).

### Deterministic UUID Generation

File UUIDs are generated via **SHA256 hash** of canonical file paths:

```python
def _generate_deterministic_uuid(file_path: str, repo_root: str) -> UUID:
    """Generate deterministic UUID from file path.

    Canonicalization rules:
    - Path separators: Always forward slash `/` (POSIX-style)
    - Case: Preserve original case (no normalization)
    - Encoding: UTF-8
    - Format: `{repo_root}::{file_path}`
    """
    canonical = f"{repo_root}::{file_path}"
    hash_bytes = hashlib.sha256(canonical.encode("utf-8")).digest()
    return UUID(bytes=hash_bytes[:16])
```

**Cross-Platform Consistency**:
- Windows path `C:\repo\src\file.py` → Normalized to `C:/repo::src/file.py`
- Linux path `/repo/src/file.py` → Normalized to `/repo::src/file.py`
- Same relative path produces same UUID on all platforms

### Stable Ordering

All arrays and dictionaries are **sorted deterministically**:
- `languages`: Sorted by language name (alphabetical)
- `file_index`: Keys sorted by UUID (lexicographic)
- `files`: Sorted by file path (alphabetical)
- `imports`: Sorted alphabetically per file
- `dependencies`: Sorted by UUID per file
- `scripts`: Keys sorted alphabetically

### Non-Deterministic Fields

These fields change on each snapshot and should be ignored when comparing snapshots:
- `snapshot_id`: New UUID v4 on each snapshot (top-level)
- `created_at`: Current timestamp (top-level)
- `analyzed_at`: Analysis timestamp (structure)

**Comparison Helper** (from tests):
```python
def strip_timestamps(snapshot_dict: dict) -> dict:
    """Remove timestamp fields for stable comparison."""
    snapshot = snapshot_dict.copy()
    snapshot.pop("snapshot_id", None)
    snapshot.pop("created_at", None)
    if "structure" in snapshot:
        snapshot["structure"].pop("analyzed_at", None)
    return snapshot
```

## Contract Freeze (Semantic Versioning Commitment)

### v1.x Compatibility Promise

Under schema version `1.x.y`, the following are **guaranteed stable**:

**No Breaking Changes**:
- Field names will NOT be renamed
- Field types will NOT change
- Required fields will NOT become optional or vice versa
- Enum values will NOT be removed
- Array/object structures will NOT be reordered

**Allowed Additive Changes** (minor version bumps):
- New optional fields may be added
- New enum values may be added
- New tooling detections may be added
- Documentation clarifications

**Patch Version Bumps** (bug fixes only):
- Fix incorrect detection logic
- Fix path normalization bugs
- Fix sorting inconsistencies
- No schema changes

### Breaking Changes → v2.0.0

Schema-breaking changes require major version bump:
- Renaming existing fields
- Changing field types
- Removing fields or enum values
- Changing deterministic UUID algorithm
- Changing sort order semantics

**Migration Path**: v1 and v2 schemas will coexist. Consumers can check `schema_version` field and handle accordingly.

### Version Check

```python
from intentgraph.snapshot import RepoSnapshot

snapshot = RepoSnapshot.parse_file("snapshot.json")

if snapshot.schema_version.startswith("1."):
    # v1 schema - stable contract
    process_v1_snapshot(snapshot)
elif snapshot.schema_version.startswith("2."):
    # v2 schema - handle breaking changes
    process_v2_snapshot(snapshot)
else:
    raise ValueError(f"Unsupported schema version: {snapshot.schema_version}")
```

## Implementation Details

### Architecture

RepoSnapshot follows Clean Architecture:
- **Domain**: `models.py` - Pydantic schemas (StructureSnapshot, RuntimeSnapshot, RepoSnapshot)
- **Application**: `builder.py` - RepoSnapshotBuilder orchestrates analysis
- **Infrastructure**: `runtime.py` - RuntimeDetector for environment discovery

**Dependencies**:
- **IntentGraph Core**: Reuses `RepositoryAnalyzer` for code structure analysis
- **Pydantic**: Schema validation and JSON serialization
- **Standard Library**: hashlib, json, pathlib (no external runtime deps)

### RuntimeDetector Behavior

`RuntimeDetector` performs **discovery-only** detection:

**Package Manager Detection**:
1. Searches for lockfiles in priority order (pnpm-lock.yaml, package-lock.json, etc.)
2. Returns first match as `PackageManager` enum
3. Falls back to `UNKNOWN` if no lockfiles found
4. Never executes package manager commands

**Version Extraction**:
- **Node.js**: Reads `engines.node` from package.json, falls back to .nvmrc
- **Python**: Parses `requires-python` from pyproject.toml (e.g., ">=3.12" → "3.12")
- Never invokes `node --version` or `python --version`

**Tooling Discovery**:
- Searches common config file names (tsconfig.json, .eslintrc.json, pyproject.toml)
- Checks repository root and standard config directories
- Applies precedence rules (dedicated files > pyproject.toml sections)
- Records file path, does not validate config syntax

**Script Extraction**:
- Reads `scripts` section from package.json (JavaScript/TypeScript)
- Reads `[project.scripts]` or `[tool.poetry.scripts]` from pyproject.toml (Python)
- Returns as key-value dictionary
- Does not execute or validate scripts

### Snapshot Size

**Typical sizes** (empirical):
- Minimal Python project (2 files): ~2 KB
- Small Node.js project (10-20 files): ~10-15 KB
- Medium multi-language project (50-100 files): ~30-50 KB
- Large repository (200+ files): ~80-150 KB

**Size Mitigation**:
- Structure analysis is AST-based (no raw code included)
- Only key metadata extracted per file
- Test files excluded by default (`include_tests=False`)

**Future**: If snapshots exceed AI context limits (~200KB), consider:
- Using IntentGraph's clustering mode for large repos
- Incremental snapshots (file deltas only)
- Compression (gzip reduces JSON by ~70%)

## Testing

### Test Coverage

**Snapshot Module**: 29/29 tests passing (100%)
- `test_determinism.py`: 9 tests - UUID stability, idempotence, cross-platform consistency
- `test_structure.py`: 6 tests - File detection, dependencies, imports, language detection
- `test_runtime.py`: 6 tests - Package manager, workspace, tooling, script detection
- `test_edge_cases.py`: 8 tests - Malformed configs, empty repos, unicode paths, JSON serialization

### Test Fixtures

Located in `tests/test_snapshot/fixtures/`:
- `structure_only/`: Minimal Python files (main.py, utils.py)
- `node_pnpm/`: TypeScript project with pnpm workspace
- `python_poetry/`: Python project with Poetry and tooling configs
- `malformed_toml/`: Intentionally broken TOML for error handling
- `mixed_tooling/`: Multiple config files to test precedence rules

Fixtures are **session-initialized** as git repositories via pytest `autouse` fixture in `conftest.py`.

### Running Tests

```bash
# Run all snapshot tests
pytest tests/test_snapshot/ -v

# Run specific test file
pytest tests/test_snapshot/test_determinism.py -v

# Run with coverage
pytest tests/test_snapshot/ --cov=intentgraph.snapshot --cov-report=term-missing
```

## Examples

### Example 1: Basic Snapshot Generation

```python
from pathlib import Path
from intentgraph.snapshot import RepoSnapshotBuilder

# Analyze current directory
builder = RepoSnapshotBuilder(Path.cwd())
snapshot = builder.build()

# Print summary
print(f"Schema: {snapshot.schema_version}")
print(f"Files: {len(snapshot.structure.files)}")
print(f"Languages: {', '.join(lang.language for lang in snapshot.structure.languages)}")
print(f"Package Manager: {snapshot.runtime.package_manager}")

# Save to file
json_str = builder.build_json(indent=2)
Path("repo-snapshot.json").write_text(json_str)
```

### Example 2: Comparing Snapshots (Change Detection)

```python
import json
from pathlib import Path
from intentgraph.snapshot import RepoSnapshotBuilder

def strip_timestamps(data: dict) -> dict:
    """Remove non-deterministic fields."""
    data = data.copy()
    data.pop("snapshot_id", None)
    data.pop("created_at", None)
    if "structure" in data:
        data["structure"].pop("analyzed_at", None)
    return data

# Generate snapshots at two points in time
builder = RepoSnapshotBuilder(Path.cwd())

snapshot1 = json.loads(builder.build_json())
# ... make code changes ...
snapshot2 = json.loads(builder.build_json())

# Compare (ignoring timestamps)
s1 = strip_timestamps(snapshot1)
s2 = strip_timestamps(snapshot2)

if s1 == s2:
    print("No structural changes detected")
else:
    # Detect what changed
    if s1["structure"]["files"] != s2["structure"]["files"]:
        print("File structure changed")
    if s1["runtime"] != s2["runtime"]:
        print("Runtime configuration changed")
```

### Example 3: Including Test Files

```python
from pathlib import Path
from intentgraph import RepositoryAnalyzer
from intentgraph.snapshot import RepoSnapshotBuilder

# Create custom analyzer that includes test files
analyzer = RepositoryAnalyzer(
    include_tests=True,  # Include files matching test patterns
    workers=4
)

# Generate snapshot with tests included
repo_path = Path("/path/to/repo")
builder = RepoSnapshotBuilder(repo_path)
analysis_result = analyzer.analyze(repo_path)
snapshot = builder.build(analysis_result=analysis_result)

print(f"Total files (including tests): {len(snapshot.structure.files)}")

# Filter to just test files in output
test_files = [
    f for f in snapshot.structure.files
    if "test" in f.path.lower()
]
print(f"Test files: {len(test_files)}")
```

### Example 4: Extracting Runtime Scripts

```python
from pathlib import Path
from intentgraph.snapshot import RepoSnapshotBuilder

builder = RepoSnapshotBuilder(Path.cwd())
snapshot = builder.build()

# List all available scripts
if snapshot.runtime.scripts:
    print("Available scripts:")
    for name, command in sorted(snapshot.runtime.scripts.items()):
        print(f"  {name}: {command}")
else:
    print("No scripts found")

# Check for specific script
if "test" in snapshot.runtime.scripts:
    print(f"Test command: {snapshot.runtime.scripts['test']}")
```

## Limitations

### Current Limitations

1. **Language Support**: Full analysis for Python only; JavaScript/TypeScript get basic parsing; Go is minimal
2. **Dependency Resolution**: Import statements extracted but not resolved to actual files for JS/TS
3. **Complexity Metrics**: Only calculated for Python (JavaScript/TypeScript return 0)
4. **Binary Files**: Ignored (no analysis of compiled code, images, PDFs, etc.)
5. **Large Files**: Files >10MB may cause memory issues (no streaming support yet)
6. **Nested Repos**: Submodules and nested git repos may cause conflicts

### Known Issues

- **Pydantic Deprecations**: Uses Pydantic v2 with v1-style validators (warnings present, will be fixed in v1.1.0)
- **Windows Paths**: UUIDs use POSIX-style internally but should work cross-platform (tested on Linux/WSL)

### Not Planned for v1.x

These features require breaking changes and will come in v2.0.0:
- Streaming analysis for very large repositories
- Incremental snapshot updates (file deltas)
- Deep semantic analysis (beyond AST)
- Multi-repo workspace snapshots
- Snapshot compression (gzip)

## Changelog

### v1.0.0 (2026-02-17)

**Initial release** of RepoSnapshot v1 schema.

**Features**:
- Deterministic snapshot generation with stable UUIDs
- Structure analysis (files, languages, dependencies, imports)
- Runtime detection (package managers, tooling, scripts)
- Cross-platform path normalization
- Comprehensive test suite (29 tests, 100% passing)

**Supported Languages**:
- Python: Full analysis (AST, complexity, maintainability)
- JavaScript/TypeScript: Basic analysis (imports, exports)
- Go: Minimal analysis (file detection only)

**Supported Package Managers**:
- Node.js: pnpm, npm, yarn, bun
- Python: poetry, pip, pipenv, conda

**Supported Tooling**:
- JavaScript/TypeScript: TypeScript, Vitest, Jest, ESLint, Prettier
- Python: pytest, ruff, mypy, black

---

**Last Updated**: 2026-02-17
**Schema Version**: 1.0.0
**Module Version**: intentgraph 0.3.1
