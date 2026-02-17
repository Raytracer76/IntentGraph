# IntentGraph Examples

Real-world outputs from IntentGraph analyzing **its own codebase** (meta-analysis).

## Example Directories

### 📊 [basic_analysis/](basic_analysis/)

Traditional IntentGraph analysis outputs at different detail levels.

**Contents**:
- `intentgraph_minimal.json` (~20 KB) - AI-optimized minimal output
- `intentgraph_medium.json` (~15 KB) - Balanced detail with complexity
- `intentgraph_full.json` (~6 KB) - Complete analysis (truncated)
- `intentgraph_traditional.json` (~29 KB) - Original format with random UUIDs

**Best for**: Understanding IntentGraph's core analysis capabilities and output levels.

### 🔒 [snapshot_v1/](snapshot_v1/)

RepoSnapshot v1 deterministic output with runtime detection.

**Contents**:
- `intentgraph_snapshot_v1.json` (~46 KB) - Deterministic snapshot with runtime info

**Best for**: Version-controlled snapshots, change tracking, AI agent context with stable UUIDs.

## Quick Comparison

| Directory | Output Type | Size | Files | Deterministic | Runtime Info |
|-----------|-------------|------|-------|---------------|--------------|
| **basic_analysis/** | Traditional | 20-29 KB | 48-51 | ❌ No | ❌ No |
| **snapshot_v1/** | RepoSnapshot v1 | 46 KB | 80 | ✅ Yes | ✅ Yes |

## What's Analyzed

All examples analyze the **intentgraph repository**:
- **Languages**: Python (primary), JavaScript, TypeScript
- **Files**: ~50-80 depending on test file inclusion
- **Structure**: Clean Architecture (Domain, Application, Infrastructure layers)
- **Runtime**: Python 3.12+, pip package manager, pytest/ruff/mypy tooling

## Output Philosophy

**No Python Scripts**: Examples contain only actual outputs, not code to generate them. This keeps examples focused on results, not implementation.

**Real Data**: All outputs are unmodified, real analysis of intentgraph codebase. No synthetic or contrived examples.

**Up-to-date**: Regenerated with each major release to reflect current codebase state.

## Choosing the Right Output

### Use Traditional Analysis When:
- ✅ Need real-time exploration
- ✅ Want detailed symbol information
- ✅ Performing one-time analysis
- ✅ Don't need version control

**→ See `basic_analysis/`**

### Use RepoSnapshot v1 When:
- ✅ Need deterministic, reproducible output
- ✅ Storing snapshots in version control
- ✅ Tracking changes over time
- ✅ Need runtime environment info
- ✅ Cross-platform consistency required
- ✅ Providing stable context to AI agents

**→ See `snapshot_v1/`**

## Documentation

- **Traditional Analysis**: [README.md](../README.md)
- **RepoSnapshot v1**: [docs/reposnapshot-v1.md](../docs/reposnapshot-v1.md)
- **CLI Usage**: Run `intentgraph --help`

## Generating Your Own Outputs

### Traditional Analysis
```python
from pathlib import Path
from intentgraph import RepositoryAnalyzer

analyzer = RepositoryAnalyzer()
result = analyzer.analyze(Path("/path/to/repo"))
print(f"Files: {len(result.files)}")
```

### RepoSnapshot v1
```python
from pathlib import Path
from intentgraph.snapshot import RepoSnapshotBuilder

builder = RepoSnapshotBuilder(Path("/path/to/repo"))
snapshot = builder.build()
json_output = builder.build_json(indent=2)
```

## Example Use Cases

### Change Tracking
```bash
# Generate baseline snapshot
intentgraph . > before.json

# Make code changes...

# Generate new snapshot and compare
intentgraph . > after.json
diff before.json after.json  # Note: Use RepoSnapshot v1 for deterministic diffs
```

### AI Agent Context
Use `intentgraph_minimal.json` - fits within AI token limits (~200KB) and provides enough context for code understanding.

### Code Quality Assessment
Use `intentgraph_medium.json` - includes complexity scores to identify hotspots.

### Runtime Documentation
Use `intentgraph_snapshot_v1.json` - captures package manager, tooling, and version requirements.

---

**Last Updated**: 2026-02-17
**IntentGraph Version**: 0.3.1
**Examples Generated From**: intentgraph repository (self-analysis)
