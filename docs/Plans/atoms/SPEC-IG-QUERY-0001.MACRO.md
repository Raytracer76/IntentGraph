# SPEC-IG-QUERY-0001 — Macro Sections

## M020 — SPEC-IG-QUERY-0001 — IntentGraph AI Query Interface (CLI)

---

## M030 — 1. Header

```
plan_id: SPEC-IG-QUERY-0001
related_spec_ids: []
generated_at_utc: 2026-02-21T00:00:00Z
author_agent: claude-sonnet-4-6
determinism_mode: true
```

---

## M010 — 2. Goal

Add a `query` sub-command group and a `cache` sub-command group to the
`intentgraph` CLI so that AI agents can interrogate a repository's analysis
results through discrete, machine-readable commands without re-analysing the
repository on every invocation.

---

## M030 — 3. Scope

in_scope:
- `src/intentgraph/cache.py` — cache read, write, and staleness logic
- `src/intentgraph/query_engine.py` — in-memory query indices and query methods
- `src/intentgraph/cli.py` — `query` and `cache` Typer sub-app additions
- `tests/test_cache.py` — unit tests for cache module
- `tests/test_query_engine.py` — unit tests for query engine
- `tests/test_query_cli.py` — CLI integration tests for all new sub-commands
- JSON output schema for all new commands

out_of_scope:
- Changes to the existing `analyze` command behaviour
- Changes to domain models (`FileInfo`, `CodeSymbol`, `AnalysisResult`)
- Changes to the RepoSnapshot v1 snapshot pipeline
- MCP server integration
- Natural-language query parsing (the existing `ai/` scaffolding)
- Network or remote repository support

---

## M070 — 4. External Dependencies

```yaml
external_dependencies: []
```

---

## M030 — 5. Preconditions

- The `intentgraph` package MUST be installed with all existing tests passing.
- The `AnalysisResult` domain model MUST expose `files: list[FileInfo]`
  where each `FileInfo` carries `path`, `id`, `sha256`, `dependencies`,
  `symbols`, `exports`, `language`, and `loc`.
- The `RepositoryAnalyzer.analyze(repo_path)` method MUST be callable and
  MUST return an `AnalysisResult`.
- The existing Typer `app` object in `cli.py` MUST be importable and MUST
  accept `add_typer()` calls without modification to existing commands.

---

## M030 — 6. Gates

entry_gate:
  condition: All existing tests pass (`pytest` exits 0).
  verification_method: Run `pytest` and inspect exit code.
  failure_behavior: Do not begin implementation until all existing tests pass.

mid_run_gates:
  - id: MG-01
    condition: >
      `tests/test_cache.py` passes with 100% coverage of `cache.py` before
      `query_engine.py` is written.
    verification_method: Run `pytest tests/test_cache.py --cov=intentgraph.cache`.
    failure_behavior: Fix `cache.py` before proceeding to query engine.
  - id: MG-02
    condition: >
      `tests/test_query_engine.py` passes with 100% coverage of
      `query_engine.py` before CLI wiring is written.
    verification_method: Run `pytest tests/test_query_engine.py --cov=intentgraph.query_engine`.
    failure_behavior: Fix `query_engine.py` before proceeding to CLI.

exit_gate:
  condition: >
    `pytest` exits 0 across all test files including new tests.
    `intentgraph query --help` lists all seven sub-commands.
    `intentgraph cache --help` lists all three sub-commands.
    All new CLI commands emit valid JSON to stdout on a fixture repository.
  verification_method: >
    Run `pytest`, then run each command against `tests/fixtures/` and
    validate output with `python3 -c "import json,sys; json.load(sys.stdin)"`.
  failure_behavior: Do not mark implementation complete until exit gate passes.

---

## M030 — 7. Tasks



## M030 — T-01 — Implement `cache.py`

id: T-01
description: >
  Create `src/intentgraph/cache.py`. The module MUST expose a `CacheManager`
  class. `CacheManager.__init__` MUST accept `repo_path: Path`. The cache file
  MUST be stored at `<repo_path>/.intentgraph/cache.json`. `CacheManager.load`
  MUST return a cached `AnalysisResult` if the cache is fresh, or `None` if the
  cache is absent or stale. `CacheManager.save` MUST accept an `AnalysisResult`
  and MUST write it atomically (write to a temp file, then rename). Staleness
  detection MUST compare the `sha256` field of each `FileInfo` in the cached
  result against the current SHA-256 digest of the corresponding file on disk.
  A cache MUST be considered stale if any tracked file has changed its SHA-256
  digest or if any tracked file no longer exists. The cache format MUST be a
  JSON object with a `schema_version` field set to `"1"` and a `result` field
  containing the serialised `AnalysisResult`. `CacheManager` MUST expose a
  `clear` method that deletes the cache file if it exists.
  `CacheManager` MUST expose a `status` method that returns a dict containing
  the keys `exists` (bool), `stale` (bool), `file_count` (int), and `cache_path` (str).
  The module MUST NOT import from `src/intentgraph/ai/`.
expected_result: `cache.py` created; all `test_cache.py` tests pass.
verification_method: `pytest tests/test_cache.py -v`

## M030 — T-02 — Implement `query_engine.py`

id: T-02
description: >
  Create `src/intentgraph/query_engine.py`. The module MUST expose a
  `QueryEngine` class. `QueryEngine.__init__` MUST accept
  `result: AnalysisResult` and MUST build the following indices synchronously
  on construction:
  - `_file_by_id: dict[UUID, FileInfo]`
  - `_file_by_path: dict[str, FileInfo]` keyed by normalised relative path string
  - `_symbol_by_name: dict[str, list[tuple[FileInfo, CodeSymbol]]]`
  - `_reverse_deps: dict[UUID, list[UUID]]` mapping each file UUID to the list
    of file UUIDs that declare it as a dependency
  `QueryEngine` MUST expose the following public methods. Each method MUST
  return a `dict` that is JSON-serialisable using the standard `json` module.

  `callers(symbol_name: str) -> dict`:
    MUST return `{"symbol": symbol_name, "callers": [...]}` where each entry
    in `callers` contains `file` (relative path), `line` (int), `context` (str or null).
    MUST search `FunctionDependency` records across all files for dependencies
    whose target symbol name matches `symbol_name` (case-sensitive exact match).
    If no callers exist the `callers` list MUST be empty.

  `dependents(file_path: str) -> dict`:
    MUST return `{"file": file_path, "dependents": [...]}` where each entry
    in `dependents` contains `file` (relative path) and `dependency_type` (str).
    MUST use `_reverse_deps` index. If no dependents exist the list MUST be empty.

  `deps(file_path: str) -> dict`:
    MUST return `{"file": file_path, "deps": [...]}` where each entry in `deps`
    contains `file` (relative path) and `dependency_type` (str).
    If no deps exist the list MUST be empty.

  `context(file_path: str) -> dict`:
    MUST return a dict with fields: `file` (str), `language` (str), `loc` (int),
    `sha256` (str), `symbols` (list), `exports` (list), `deps` (list), `dependents` (list).
    Each symbol entry MUST include: `name`, `type`, `line_start`, `line_end`,
    `signature` (or null), `is_exported` (bool), `is_private` (bool).
    If the file is not found MUST raise `FileNotFoundError`.

  `search(name_pattern: str | None, complexity_gt: int | None, lang: str | None, has_symbol: str | None) -> dict`:
    MUST return `{"query": {...}, "results": [...]}` where `query` echoes the
    filter parameters and each result contains `file` (str), `language` (str),
    `loc` (int), and `symbol_count` (int).
    `name_pattern` MUST be treated as a Python regex applied to the relative
    file path; if `None` all files pass this filter.
    `complexity_gt` filter MUST be skipped if the `FileInfo` carries no
    complexity metric; files without a metric MUST NOT be excluded.
    `lang` MUST match the `language` field of `FileInfo` (case-insensitive).
    `has_symbol` MUST match any symbol name in the file (case-sensitive exact).
    All active filters MUST be ANDed.

  `path(file_a: str, file_b: str) -> dict`:
    MUST return `{"from": file_a, "to": file_b, "path": [...], "found": bool}`.
    MUST compute the shortest directed dependency path from `file_a` to `file_b`
    using BFS over the `_file_by_path` and `_reverse_deps` indices.
    If no path exists `found` MUST be `false` and `path` MUST be an empty list.
    If `file_a` equals `file_b` `found` MUST be `true` and `path` MUST contain
    exactly one entry.

  `symbols(file_path: str) -> dict`:
    MUST return `{"file": file_path, "symbols": [...]}` where each symbol entry
    contains `name`, `type`, `line_start`, `line_end`, `signature` (or null),
    `is_exported` (bool), `is_private` (bool).
    If the file is not found MUST raise `FileNotFoundError`.

  The module MUST NOT import from `src/intentgraph/ai/`.
expected_result: `query_engine.py` created; all `test_query_engine.py` tests pass.
verification_method: `pytest tests/test_query_engine.py -v`

## M020 — T-03 — Wire CLI sub-commands

id: T-03
description: >
  Add two Typer sub-applications to `src/intentgraph/cli.py`.

  Sub-application `query_app` MUST be mounted on the main `app` with name
  `"query"` and help text `"Query cached repository analysis."`.
  Sub-application `cache_app` MUST be mounted on the main `app` with name
  `"cache"` and help text `"Manage the analysis cache."`.

  All `query_app` commands MUST accept a `--repo` option of type `Path`
  defaulting to `Path(".")` that specifies the repository root.
  All `query_app` commands MUST: (1) call `CacheManager(repo).load_or_analyze()`
  to obtain an `AnalysisResult`, transparently re-analysing if the cache is
  absent or stale; (2) construct a `QueryEngine(result)`; (3) call the
  appropriate engine method; (4) print the result as JSON to stdout using
  `json.dumps` with `indent=2`; (5) exit with code 0 on success.
  On any error, commands MUST print a JSON error object
  `{"error": "<message>"}` to stderr and MUST exit with a non-zero code.

  `CacheManager` MUST expose `load_or_analyze() -> AnalysisResult` defined as follows.
  MUST call `load()`; if `None` MUST call `RepositoryAnalyzer().analyze(repo_path)`
  then `save(result)` then return the result.

  `query_app` MUST expose exactly these seven sub-commands: callers, dependents, deps, context, search, path, symbols.

  `callers <symbol>`:
    positional argument `symbol: str`. Calls `engine.callers(symbol)`.

  `dependents <file>`:
    positional argument `file: str`. Calls `engine.dependents(file)`.

  `deps <file>`:
    positional argument `file: str`. Calls `engine.deps(file)`.

  `context <file>`:
    positional argument `file: str`. Calls `engine.context(file)`.

  `search`:
    options `--name-matches: str | None`, `--complexity-gt: int | None`,
    `--lang: str | None`, `--has-symbol: str | None`.
    At least one option MUST be provided; if none are provided the command
    MUST print a JSON error and exit non-zero.
    Calls `engine.search(name_pattern, complexity_gt, lang, has_symbol)`.

  `path <file-a> <file-b>`:
    positional arguments `file_a: str`, `file_b: str`.
    Calls `engine.path(file_a, file_b)`.

  `symbols <file>`:
    positional argument `file: str`. Calls `engine.symbols(file)`.

  `cache_app` MUST expose exactly these three sub-commands: status, warm, clear.

  `status`:
    option `--repo: Path` defaulting to `Path(".")`.
    Calls `CacheManager(repo).status()` and prints JSON to stdout.

  `warm`:
    option `--repo: Path` defaulting to `Path(".")`.
    Calls `CacheManager(repo).load_or_analyze()` (triggers re-analysis if
    stale) and prints `{"warmed": true, "file_count": <n>}` to stdout.

  `clear`:
    option `--repo: Path` defaulting to `Path(".")`.
    Calls `CacheManager(repo).clear()` and prints `{"cleared": true}` to stdout.

expected_result: >
  All CLI sub-commands registered; `intentgraph query --help` lists seven
  sub-commands; `intentgraph cache --help` lists three sub-commands.
  All `test_query_cli.py` tests pass.
verification_method: `pytest tests/test_query_cli.py -v`

---

## M020 — 8. Artifacts

| Path | Type | Determinism constraints |
|---|---|---|
| `src/intentgraph/cache.py` | py | Deterministic JSON output; atomic write via temp-rename |
| `src/intentgraph/query_engine.py` | py | All index dicts keyed by normalised string; BFS order deterministic |
| `src/intentgraph/cli.py` | py | Amended in-place; existing commands unchanged |
| `tests/test_cache.py` | py | No network; no wall-clock assertions |
| `tests/test_query_engine.py` | py | Uses fixture `AnalysisResult`; no disk I/O |
| `tests/test_query_cli.py` | py | Uses `typer.testing.CliRunner`; no network |

---

## M030 — 9. Exit Criteria

- `pytest` exits 0 with all pre-existing and new tests passing.
- `intentgraph query --help` output contains: `callers`, `dependents`, `deps`,
  `context`, `search`, `path`, `symbols`.
- `intentgraph cache --help` output contains: `status`, `warm`, `clear`.
- Every new command, when run against a fixture repository, emits valid JSON
  to stdout and exits with code 0.
- No implementation changes are pending after exit gate verification.

---

END SPEC-IG-QUERY-0001
