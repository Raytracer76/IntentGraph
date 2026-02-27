# IntentGraph

[![PyPI version](https://img.shields.io/pypi/v/intentgraph.svg)](https://pypi.org/project/intentgraph/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Static code analysis for Python, JavaScript, TypeScript, and Go — with a machine-queryable cache layer designed for AI agents.

```bash
pip install intentgraph
```

---

## What it does

IntentGraph analyses a repository's AST, dependency graph, and code metrics and writes the result to a local cache. You can then query that cache without re-running analysis:

```bash
# One-time analysis pass
intentgraph cache warm --repo .

# Query without re-analysing
intentgraph query context src/app/models.py
intentgraph query deps src/app/cli.py
intentgraph query path src/app/cli.py src/app/models.py
```

Everything outputs JSON to stdout, exits 0 on success, exits 1 with `{"error": "..."}` to stderr on failure. No side effects, no network calls.

---

## CLI reference

### `intentgraph` — analysis

```
intentgraph [OPTIONS] REPO_PATH

Options:
  --level [minimal|medium|full]          Detail level (default: minimal)
  --lang TEXT                            Languages: py,js,ts,go
  --output FILE                          Write to file instead of stdout
  --include-tests                        Include test files
  --show-cycles                          Print dependency cycles, exit 2
  --cluster                              Cluster large repos into chunks
  --cluster-mode [analysis|refactoring|navigation]
  --workers INTEGER                      Parallel workers (default: cpu count)
```

Output levels:

| Level | Size | Contents |
|-------|------|----------|
| `minimal` | ~10 KB | paths, deps, imports, basic metrics |
| `medium` | ~70 KB | + key symbols, exports, maintainability scores |
| `full` | ~340 KB | everything, including all signatures and docstrings |

For repos that exceed token limits even at `minimal`, `--cluster` splits output into ~15 KB chunks with an `index.json` navigation map.

### `intentgraph cache` — cache management

```bash
intentgraph cache warm   --repo PATH   # analyse and cache (idempotent)
intentgraph cache status --repo PATH   # {exists, stale, file_count, cache_path}
intentgraph cache clear  --repo PATH   # delete cache
```

Cache is stored at `<repo>/.intentgraph/cache.json`. Staleness is detected by comparing SHA-256 digests of tracked files.

### `intentgraph query` — structured queries

All commands accept `--repo PATH` (default: `.`).

```bash
# Symbols defined in a file
intentgraph query symbols   src/app/models.py

# Full context: language, loc, sha256, symbols, exports, deps, dependents
intentgraph query context   src/app/models.py

# Direct dependencies
intentgraph query deps      src/app/cli.py

# Reverse dependencies (who imports this file)
intentgraph query dependents src/app/models.py

# Shortest dependency path between two files (BFS)
intentgraph query path      src/app/cli.py src/app/models.py

# Call sites for a named symbol
intentgraph query callers   RepositoryAnalyzer

# Filter files by name pattern, language, symbol, complexity
intentgraph query search --name-matches ".*parser.*"
intentgraph query search --has-symbol CacheManager
intentgraph query search --lang python --complexity-gt 10
```

---

## AI agent pattern

Warm once, query many times — no re-analysis overhead:

```bash
# In your agent's setup step
intentgraph cache warm --repo /path/to/repo

# Per-query (fast — reads from cache)
intentgraph query context src/app/models.py | jq .
intentgraph query deps src/app/cli.py | jq .deps[].file
intentgraph query search --complexity-gt 15 | jq .results[].file
```

Because every output is stable JSON, an AI agent can pipe results directly into its context window at the level of detail it needs, without loading the entire codebase.

---

## Programmatic API

```python
from pathlib import Path
from intentgraph import RepositoryAnalyzer
from intentgraph.cache import CacheManager
from intentgraph.query_engine import QueryEngine

# Analysis
analyzer = RepositoryAnalyzer()
result = analyzer.analyze(Path("/path/to/repo"))

# Or use the cache layer
cm = CacheManager(Path("/path/to/repo"))
result = cm.load_or_analyze()  # uses cache if fresh, re-analyses if stale

# Query
engine = QueryEngine(result)
print(engine.context("src/app/models.py"))
print(engine.deps("src/app/cli.py"))
print(engine.search(name_pattern=r".*parser.*", lang="python"))
```

### RepoSnapshot v1 — deterministic snapshots

```python
from intentgraph.snapshot import RepoSnapshotBuilder

builder = RepoSnapshotBuilder(Path.cwd())
snapshot = builder.build()

# SHA256-based stable UUIDs — same path always produces same UUID
print(snapshot.structure.files[0].uuid)

# Runtime detection (static, no code execution)
print(snapshot.runtime.package_manager)   # pip, pnpm, poetry, ...
print(snapshot.runtime.python_version)
print(snapshot.runtime.tooling)           # pytest, ruff, mypy, ...

json_output = builder.build_json(indent=2)
```

Snapshot UUIDs are SHA256-derived — deterministic across machines and operating systems. Suitable for version-controlling snapshots or diffing them in CI.

---

## Language support

| Language | Analysis depth |
|----------|---------------|
| Python | Full AST — symbols, complexity, maintainability, exports, function-level deps |
| JavaScript | Full AST — ES6+, classes, CommonJS/ESM, complexity |
| TypeScript | Full AST — interfaces, generics, decorators, type imports |
| Go | File-level dependencies |

The `ai/` module provides a natural-language query interface and agent context management. Query parsing and intent detection work; deep semantic execution is still evolving — use the structured `query` CLI for reliable agent integration.

---

## Development

```bash
git clone https://github.com/Raytracer76/IntentGraph.git
cd IntentGraph
pip install -e ".[dev]"
pytest                                # run all tests
ruff format . && ruff check --fix .   # format + lint
mypy .                                # type check
```

Coverage threshold: 90%. Strict mypy is enforced.

---

## License

MIT — see [LICENSE](LICENSE).
