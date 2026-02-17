# Basic IntentGraph Analysis Examples

Real-world outputs from IntentGraph analyzing its own codebase.

## Output Levels

IntentGraph provides three output levels optimized for different use cases:

### 1. Minimal Output (`intentgraph_minimal.json`)

**Size**: ~20 KB
**Purpose**: AI-optimized for fitting within context windows (~200KB limit)

**Contains**:
- File paths and languages
- Lines of code per file
- Import statements (first 10)
- Dependency counts

**Best for**:
- AI agent context
- Quick codebase overview
- Fitting multiple files in limited tokens
- Initial exploration

**Example structure**:
```json
{
  "output_level": "minimal",
  "total_files": 51,
  "languages": {
    "python": {"file_count": 40, "total_bytes": 328211}
  },
  "files": [
    {
      "path": "src/intentgraph/cli.py",
      "language": "python",
      "loc": 150,
      "imports": ["typer", "rich", "pathlib"],
      "dependencies_count": 5
    }
  ]
}
```

### 2. Medium Output (`intentgraph_medium.json`)

**Size**: ~15 KB
**Purpose**: Balanced detail with key insights

**Contains**:
- Everything from minimal
- Complexity scores
- Key symbols (first 5 per file)
- Export counts

**Best for**:
- Code quality assessment
- Finding high-complexity areas
- Understanding key abstractions
- Balanced AI context

**Example structure**:
```json
{
  "output_level": "medium",
  "files": [
    {
      "path": "src/intentgraph/cli.py",
      "complexity": 15,
      "key_symbols": [
        {"name": "main", "type": "function"},
        {"name": "analyze_command", "type": "function"}
      ],
      "exports_count": 3
    }
  ]
}
```

### 3. Full Output (`intentgraph_full.json`)

**Size**: ~6 KB (truncated to 10 files for demo)
**Purpose**: Complete structural analysis

**Contains**:
- Everything from medium
- File UUIDs
- Maintainability index
- Complete imports and dependencies
- Full symbol and export counts

**Best for**:
- Deep code analysis
- Refactoring planning
- Understanding dependencies
- Academic research

**Example structure**:
```json
{
  "output_level": "full",
  "files": [
    {
      "id": "f7a8b3c4-d5e6-47f8-9012-3456789abcde",
      "path": "src/intentgraph/cli.py",
      "complexity": 15,
      "maintainability": 72.5,
      "symbols_count": 12,
      "exports_count": 3
    }
  ]
}
```

### 4. Traditional Format (`intentgraph_traditional.json`)

**Size**: ~29 KB
**Purpose**: Original IntentGraph output with detailed metadata

**Contains**:
- Random UUIDs (uuid4)
- Full language summary
- Detailed per-file analysis
- Symbol-level information
- Import and dependency tracking

**Note**: This format is **not deterministic** - UUIDs change on each run. Use RepoSnapshot v1 for deterministic, version-controlled output.

## Size Comparison

| Level | Size | Files Included | Use Case |
|-------|------|----------------|----------|
| **Minimal** | ~20 KB | All (51) | AI context, quick overview |
| **Medium** | ~15 KB | First 20 | Balanced detail |
| **Full** | ~6 KB | First 10 (truncated) | Deep analysis |
| **Traditional** | ~29 KB | All (48, excludes tests) | Legacy format |

**Note**: Full output for entire intentgraph repo would be ~340 KB. Shown outputs are truncated for practical file sizes.

## When to Use Each Level

### Use Minimal When:
- ✅ Working with AI agents (limited context)
- ✅ Need quick codebase overview
- ✅ Analyzing large repositories
- ✅ Token budget is constrained

### Use Medium When:
- ✅ Assessing code quality
- ✅ Finding complexity hotspots
- ✅ Understanding key abstractions
- ✅ Balanced detail/size tradeoff

### Use Full When:
- ✅ Deep structural analysis needed
- ✅ Planning major refactoring
- ✅ Understanding all dependencies
- ✅ No size constraints

### Use Traditional When:
- ✅ Need original IntentGraph format
- ✅ Real-time exploration (don't need determinism)
- ✅ Want symbol-level details
- ✅ Not storing in version control

## Generating These Outputs

```python
from pathlib import Path
from intentgraph import RepositoryAnalyzer

analyzer = RepositoryAnalyzer()
result = analyzer.analyze(Path.cwd())

# Result contains all data - format as needed for your use case
print(f"Files analyzed: {len(result.files)}")
print(f"Languages: {list(result.language_summary.keys())}")
```

For deterministic, version-controlled output, use **RepoSnapshot v1** instead (see `../snapshot_v1/`).

---

**Last Updated**: 2026-02-17
**IntentGraph Version**: 0.3.1
**Repository**: intentgraph (self-analysis)
