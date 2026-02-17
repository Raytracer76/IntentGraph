# RepoSnapshot v1 Example

Real-world RepoSnapshot v1 output from IntentGraph analyzing its own codebase.

## Output File

**`intentgraph_snapshot_v1.json`** (~46 KB)

Deterministic snapshot combining code structure analysis with runtime environment detection.

## What's Included

### Structure Section
- **80 files analyzed** (includes test files)
- **Deterministic UUIDs** (SHA256-based, never change for same path)
- **Sorted arrays** (languages, files, imports, dependencies)
- **File index** (bidirectional UUID ↔ path mapping)
- **Cross-platform consistency** (Windows/Linux produce identical output)

### Runtime Section
- **Package Manager**: pip
- **Python Version**: >=3.12
- **Tooling Detected**:
  - pytest (from pyproject.toml)
  - ruff (from pyproject.toml)
  - mypy (from pyproject.toml)
- **Scripts**: (none - intentgraph has no scripts section)

## Schema Structure

```json
{
  "schema_version": "1.0.0",
  "snapshot_id": "7a44484a-15c4-4a42-ae2a-57bf42b931e7",
  "created_at": "2026-02-17T09:26:04.413887Z",
  "structure": {
    "root_path": "/path/to/intentgraph",
    "analyzed_at": "2026-02-17T09:26:04.395201Z",
    "languages": [...],
    "file_index": {
      "e0c8681a-5ec1-9106-384c-eaa1c315da83": "src/intentgraph/cli.py"
    },
    "files": [...]
  },
  "runtime": {
    "package_manager": "pip",
    "python_version": ">=3.12",
    "tooling": {...},
    "scripts": {}
  }
}
```

## Key Features

### Deterministic UUIDs
```
File: src/intentgraph/cli.py
UUID: e0c8681a-5ec1-9106-384c-eaa1c315da83

Same path → Same UUID every time
Cross-platform → Windows and Linux produce identical UUID
```

**How it works**:
```python
canonical = f"{repo_root}::{file_path}"  # POSIX-style paths
hash_bytes = hashlib.sha256(canonical.encode("utf-8")).digest()
uuid = UUID(bytes=hash_bytes[:16])
```

### Stable Ordering
All arrays are deterministically sorted:
- **Languages**: Alphabetically by language name
- **File Index**: By UUID (lexicographic)
- **Files**: Alphabetically by path
- **Imports**: Alphabetically per file
- **Dependencies**: By UUID per file

### Runtime Detection (No Execution)
Static analysis only - reads config files as text:
- Searches for lockfiles (pnpm-lock.yaml, package-lock.json, poetry.lock, etc.)
- Parses version requirements from package.json/pyproject.toml
- Discovers tooling configs (tsconfig.json, .eslintrc, pyproject.toml)
- Extracts scripts from package.json or pyproject.toml

**Never executes**:
- No `python --version` or `node --version`
- No package manager commands
- No script execution

## Comparison with Traditional Output

| Aspect | Traditional | RepoSnapshot v1 |
|--------|-------------|-----------------|
| **Files** | 48 (excludes tests) | 80 (includes tests) |
| **UUIDs** | Random (uuid4) | Deterministic (SHA256) |
| **Ordering** | May vary | Stable (sorted) |
| **Runtime Info** | None | Full detection |
| **Version Control** | ❌ Not suitable | ✅ Designed for it |
| **Cross-platform** | ⚠️ May differ | ✅ Identical |
| **Schema Version** | None | 1.0.0 (frozen) |

## Use Cases

### ✅ Perfect For:
- Version control and change tracking
- CI/CD pipelines (snapshot before/after builds)
- AI agent context (stable, reproducible)
- Documentation generation
- Dependency auditing
- Configuration discovery
- Cross-platform development

### ⚠️ Less Suitable For:
- Deep symbol-level analysis (use traditional format)
- Real-time exploration (determinism overhead unnecessary)
- When you need Python-specific metrics only

## Contract Freeze

**Schema v1.x.y** is frozen:
- Field names will NOT be renamed
- Field types will NOT change
- Only additive changes in minor versions (new optional fields)
- Breaking changes require v2.0.0

**Check version in code**:
```python
from intentgraph.snapshot import RepoSnapshot

snapshot = RepoSnapshot.parse_file("intentgraph_snapshot_v1.json")

if snapshot.schema_version.startswith("1."):
    # v1.x - stable contract
    process_v1(snapshot)
```

## Generating This Output

```python
from pathlib import Path
from intentgraph.snapshot import RepoSnapshotBuilder

builder = RepoSnapshotBuilder(Path.cwd())
snapshot = builder.build()

# Serialize to JSON
json_output = builder.build_json(indent=2)
Path("snapshot.json").write_text(json_output)

# Access data
print(f"Files: {len(snapshot.structure.files)}")
print(f"Package Manager: {snapshot.runtime.package_manager}")
print(f"Tooling: {snapshot.runtime.tooling}")
```

## Documentation

See **[docs/reposnapshot-v1.md](../../docs/reposnapshot-v1.md)** for complete documentation:
- Full schema specification
- Determinism guarantees
- Configuration options (`include_tests`)
- Security notes
- Contract freeze details

---

**Last Updated**: 2026-02-17
**Schema Version**: 1.0.0
**IntentGraph Version**: 0.3.1
**Repository**: intentgraph (self-analysis)
