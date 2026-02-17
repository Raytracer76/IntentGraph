# IntentGraph Repository Analysis Examples

This directory contains real-world examples of IntentGraph analyzing **itself** - showing both the traditional IntentGraph output and the new RepoSnapshot v1 format.

## Contents

- **`intentgraph_traditional.json`** - Traditional IntentGraph analysis output (~29 KB)
- **`intentgraph_snapshot_v1.json`** - RepoSnapshot v1 format (~46 KB)
- **`generate_traditional_analysis.py`** - Script to generate traditional output
- **`generate_snapshot_v1.py`** - Script to generate snapshot output
- **`compare_outputs.py`** - Comparison tool showing differences

## Output Formats

### Traditional IntentGraph (`intentgraph_traditional.json`)

**Purpose**: Deep code structure analysis for real-time exploration.

**What it includes**:
- Random UUIDs (uuid4) for files
- Detailed symbol information (functions, classes, variables)
- Python-specific metrics (complexity, maintainability index)
- Import statements and file dependencies
- Language statistics

**Best for**:
- Interactive code exploration
- Deep structural analysis
- Understanding code organization
- Symbol-level queries

**Limitations**:
- ❌ Not deterministic (UUIDs change on each run)
- ❌ Not suitable for version control or change tracking
- ❌ No runtime environment information

### RepoSnapshot v1 (`intentgraph_snapshot_v1.json`)

**Purpose**: Deterministic, version-controlled snapshot for change tracking and AI agents.

**What it includes**:
- **Structure**:
  - Deterministic UUIDs (SHA256-based) for files
  - File metadata (path, language, LOC, complexity)
  - Stable ordering (all arrays sorted)
  - File index (UUID ↔ path bidirectional mapping)
  - Import statements and dependencies
- **Runtime**:
  - Package manager (pip, poetry, npm, pnpm, etc.)
  - Workspace type (monorepo detection)
  - Version requirements (Python, Node.js)
  - Tooling configs (pytest, mypy, ruff, TypeScript, ESLint, etc.)
  - Available scripts (npm scripts, pyproject.toml scripts)

**Best for**:
- Version control and change tracking
- Cross-platform consistency (Windows/Linux)
- AI agent context (stable, reproducible)
- Runtime environment documentation
- Configuration discovery

**Guarantees**:
- ✅ Deterministic UUIDs (same path → same UUID)
- ✅ Stable ordering (reproducible JSON)
- ✅ Schema versioning (v1.x contract frozen)
- ✅ No code execution (static analysis only)

## Quick Start

### Generate Outputs

```bash
# Generate traditional IntentGraph analysis
python generate_traditional_analysis.py

# Generate RepoSnapshot v1
python generate_snapshot_v1.py

# Compare both outputs
python compare_outputs.py
```

### Use Programmatically

**Traditional Analysis**:
```python
from pathlib import Path
from intentgraph import RepositoryAnalyzer

analyzer = RepositoryAnalyzer()
result = analyzer.analyze(Path.cwd())

print(f"Files: {len(result.files)}")
print(f"Languages: {result.language_summary.keys()}")
```

**RepoSnapshot v1**:
```python
from pathlib import Path
from intentgraph.snapshot import RepoSnapshotBuilder

builder = RepoSnapshotBuilder(Path.cwd())
snapshot = builder.build()

print(f"Schema: {snapshot.schema_version}")
print(f"Files: {len(snapshot.structure.files)}")
print(f"Package Manager: {snapshot.runtime.package_manager}")
print(f"Tooling: {snapshot.runtime.tooling}")
```

## Key Differences

| Feature | Traditional | RepoSnapshot v1 |
|---------|-------------|-----------------|
| **UUIDs** | Random (uuid4) | Deterministic (SHA256) |
| **Timestamps** | None | Included (but excluded from comparisons) |
| **Ordering** | May vary | Stable (sorted) |
| **Cross-platform** | ⚠️ May differ | ✅ Identical |
| **Runtime Info** | ❌ None | ✅ Full detection |
| **Symbol Details** | ✅ Detailed | ⚠️ Basic |
| **Version Control** | ❌ Not suitable | ✅ Designed for it |
| **Change Tracking** | ❌ Difficult | ✅ Built-in |
| **Schema Version** | N/A | ✅ Semantic versioning |

## Real-World Usage

### Traditional IntentGraph

**Scenario**: Exploring an unfamiliar codebase.

```python
from intentgraph import RepositoryAnalyzer

analyzer = RepositoryAnalyzer()
result = analyzer.analyze(Path("/path/to/repo"))

# Find high-complexity files
high_complexity = [
    f for f in result.files
    if f.complexity_score > 15
]

# Explore symbols in a file
for file_info in result.files:
    if file_info.path == "src/main.py":
        print(f"Symbols: {len(file_info.symbols)}")
        for symbol in file_info.symbols:
            print(f"  - {symbol.name} ({symbol.symbol_type})")
```

### RepoSnapshot v1

**Scenario**: Tracking codebase evolution over time.

```python
from pathlib import Path
from intentgraph.snapshot import RepoSnapshotBuilder
import json

def strip_timestamps(data):
    """Remove non-deterministic fields for comparison."""
    data = data.copy()
    data.pop("snapshot_id", None)
    data.pop("created_at", None)
    data["structure"].pop("analyzed_at", None)
    return data

# Generate snapshot before changes
builder = RepoSnapshotBuilder(Path.cwd())
before = json.loads(builder.build_json())

# ... make code changes ...

# Generate snapshot after changes
after = json.loads(builder.build_json())

# Compare
if strip_timestamps(before) == strip_timestamps(after):
    print("No structural changes")
else:
    print("Codebase changed:")
    if before["structure"]["files"] != after["structure"]["files"]:
        print("  - File structure modified")
    if before["runtime"] != after["runtime"]:
        print("  - Runtime configuration changed")
```

## Output Samples

### Traditional Structure
```json
{
  "repository": "/path/to/intentgraph",
  "analyzed_files": 48,
  "language_summary": {
    "python": { "file_count": 40, "total_bytes": 328211 },
    "javascript": { "file_count": 4, "total_bytes": 2876 },
    "typescript": { "file_count": 4, "total_bytes": 2941 }
  },
  "files": [
    {
      "id": "f7a8b3c4-d5e6-47f8-9012-3456789abcde",  // Random UUID
      "path": "src/intentgraph/cli.py",
      "language": "python",
      "complexity_score": 15,
      "maintainability_index": 72.5,
      "symbols_count": 12
    }
  ]
}
```

### RepoSnapshot v1 Structure
```json
{
  "schema_version": "1.0.0",
  "snapshot_id": "7a44484a-15c4-4a42-ae2a-57bf42b931e7",
  "created_at": "2026-02-17T09:26:04.413887Z",
  "structure": {
    "root_path": "/mnt/c/Users/nliga/OneDrive/Documents/Repos/intentgraph",
    "analyzed_at": "2026-02-17T09:26:04.395201Z",
    "languages": [
      { "language": "javascript", "file_count": 6, "total_bytes": 3015 },
      { "language": "python", "file_count": 68, "total_bytes": 459016 },
      { "language": "typescript", "file_count": 6, "total_bytes": 3142 }
    ],
    "file_index": {
      "e0c8681a-5ec1-9106-384c-eaa1c315da83": "src/intentgraph/cli.py"
    },
    "files": [
      {
        "uuid": "e0c8681a-5ec1-9106-384c-eaa1c315da83",  // Deterministic UUID
        "path": "src/intentgraph/cli.py",
        "language": "python",
        "lines_of_code": 150,
        "complexity": 15,
        "imports": [...],
        "dependencies": [...]
      }
    ]
  },
  "runtime": {
    "package_manager": "pip",
    "python_version": "3.12",
    "tooling": {
      "pytest": "pyproject.toml",
      "ruff": "pyproject.toml",
      "mypy": "pyproject.toml"
    },
    "scripts": {}
  }
}
```

## When to Use Each Format

### Use Traditional IntentGraph When:
- ✅ Exploring code interactively
- ✅ Need detailed symbol information
- ✅ Performing one-time analysis
- ✅ Don't need determinism
- ✅ Want Python-specific metrics (maintainability)

### Use RepoSnapshot v1 When:
- ✅ Tracking changes over time
- ✅ Version controlling snapshots
- ✅ Need cross-platform consistency
- ✅ Providing context to AI agents
- ✅ Documenting runtime environment
- ✅ Need deterministic, reproducible output
- ✅ Building on stable schema with semver guarantees

## Schema Versioning

RepoSnapshot follows **semantic versioning** with a contract freeze:

- **v1.x.y**: Schema is frozen
  - Field names will NOT be renamed
  - Field types will NOT change
  - Only additive changes allowed (new optional fields)
- **v2.0.0**: Breaking changes allowed
  - Renaming/removing fields
  - Type changes
  - Algorithm changes (UUID generation, sorting)

Check schema version in code:
```python
if snapshot.schema_version.startswith("1."):
    # v1.x - stable contract
    process_v1_snapshot(snapshot)
elif snapshot.schema_version.startswith("2."):
    # v2.x - handle breaking changes
    process_v2_snapshot(snapshot)
```

## Documentation

- **Traditional IntentGraph**: See main [README.md](../../README.md)
- **RepoSnapshot v1**: See [docs/reposnapshot-v1.md](../../docs/reposnapshot-v1.md)

## Contributing

When updating examples:
1. Regenerate outputs after significant code changes
2. Update this README if format changes
3. Ensure both traditional and snapshot examples remain in sync
4. Run comparison script to verify differences are expected

---

**Last Updated**: 2026-02-17
**IntentGraph Version**: 0.3.1
**RepoSnapshot Schema**: 1.0.0
