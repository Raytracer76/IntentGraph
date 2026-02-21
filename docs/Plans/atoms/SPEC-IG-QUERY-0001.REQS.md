# SPEC-IG-QUERY-0001 — Requirements

| requirement_id | modality | statement | anchor |
|----------------|----------|-----------|--------|
| R.SPEC-IG-QUERY-0001.s2-6.kfa477lwup | MUST | The `intentgraph` package — be installed with all existing tests passing. | SPEC-IG-QUERY-0001#s2-6:L1 |
| R.SPEC-IG-QUERY-0001.s2-6.4pwusob3gq | MUST | The `AnalysisResult` domain model — expose `files: list[FileInfo]` | SPEC-IG-QUERY-0001#s2-6:L2 |
| R.SPEC-IG-QUERY-0001.s2-6.4k3yr24cq6 | MUST | The `RepositoryAnalyzer.analyze(repo_path)` method — be callable and | SPEC-IG-QUERY-0001#s2-6:L5 |
| R.SPEC-IG-QUERY-0001.s2-6.jxe767og2y | MUST | return an `AnalysisResult`. | SPEC-IG-QUERY-0001#s2-6:L6 |
| R.SPEC-IG-QUERY-0001.s2-6.elym4qpsyq | MUST | The existing Typer `app` object in `cli.py` — be importable and MUST | SPEC-IG-QUERY-0001#s2-6:L7 |
| R.SPEC-IG-QUERY-0001.s2-6.4l4tdycuee | MUST | The existing Typer `app` object in `cli.py` MUST be importable and | SPEC-IG-QUERY-0001#s2-6:L7 |
| R.SPEC-IG-QUERY-0001.s3-9.cttpsrisk2 | MUST | Create `src/intentgraph/cache.py`. The module — expose a `CacheManager` | SPEC-IG-QUERY-0001#s3-9:L3 |
| R.SPEC-IG-QUERY-0001.s3-9.nn34z5rit3 | MUST | class. `CacheManager.__init__` — accept `repo_path: Path`. The cache file | SPEC-IG-QUERY-0001#s3-9:L4 |
| R.SPEC-IG-QUERY-0001.s3-9.jvxvw6jmwn | MUST | be stored at `<repo_path>/.intentgraph/cache.json`. `CacheManager.load` | SPEC-IG-QUERY-0001#s3-9:L5 |
| R.SPEC-IG-QUERY-0001.s3-9.3b7ruiojep | MUST | return a cached `AnalysisResult` if the cache is fresh, or `None` if the | SPEC-IG-QUERY-0001#s3-9:L6 |
| R.SPEC-IG-QUERY-0001.s3-9.5t3kppy23n | MUST | cache is absent or stale. `CacheManager.save` — accept an `AnalysisResult` | SPEC-IG-QUERY-0001#s3-9:L7 |
| R.SPEC-IG-QUERY-0001.s3-9.v42jxorgv6 | MUST | and — write it atomically (write to a temp file, then rename). Staleness | SPEC-IG-QUERY-0001#s3-9:L8 |
| R.SPEC-IG-QUERY-0001.s3-9.4txejiwhkg | MUST | detection — compare the `sha256` field of each `FileInfo` in the cached | SPEC-IG-QUERY-0001#s3-9:L9 |
| R.SPEC-IG-QUERY-0001.s3-9.awygcmzqur | MUST | A cache — be considered stale if any tracked file has changed its SHA-256 | SPEC-IG-QUERY-0001#s3-9:L11 |
| R.SPEC-IG-QUERY-0001.s3-9.tgdgisijzt | MUST | digest or if any tracked file no longer exists. The cache format — be a | SPEC-IG-QUERY-0001#s3-9:L12 |
| R.SPEC-IG-QUERY-0001.s3-9.7ryuwexv7p | MUST | containing the serialised `AnalysisResult`. `CacheManager` — expose a | SPEC-IG-QUERY-0001#s3-9:L14 |
| R.SPEC-IG-QUERY-0001.s3-9.rgw2z5mx6x | MUST | `CacheManager` — expose a `status` method that returns a dict containing | SPEC-IG-QUERY-0001#s3-9:L16 |
| R.SPEC-IG-QUERY-0001.s3-9.2sufdxwxmu | MUST NOT | The module — import from `src/intentgraph/ai/`. | SPEC-IG-QUERY-0001#s3-9:L18 |
| R.SPEC-IG-QUERY-0001.s3-10.fv2wgc3jh3 | MUST | Create `src/intentgraph/query_engine.py`. The module — expose a | SPEC-IG-QUERY-0001#s3-10:L3 |
| R.SPEC-IG-QUERY-0001.s3-10.hcmzche6wa | MUST | `QueryEngine` class. `QueryEngine.__init__` — accept | SPEC-IG-QUERY-0001#s3-10:L4 |
| R.SPEC-IG-QUERY-0001.s3-10.4qlgzzvl6j | MUST | `result: AnalysisResult` and — build the following indices synchronously | SPEC-IG-QUERY-0001#s3-10:L5 |
| R.SPEC-IG-QUERY-0001.s3-10.hrkgefwm6a | MUST | `QueryEngine` — expose the following public methods. Each method MUST | SPEC-IG-QUERY-0001#s3-10:L12 |
| R.SPEC-IG-QUERY-0001.s3-10.ejskh2s62i | MUST | `QueryEngine` MUST expose the following public methods. Each method | SPEC-IG-QUERY-0001#s3-10:L12 |
| R.SPEC-IG-QUERY-0001.s3-10.xyoue4t53a | MUST | return `{"symbol": symbol_name, "callers": [...]}` where each entry | SPEC-IG-QUERY-0001#s3-10:L16 |
| R.SPEC-IG-QUERY-0001.s3-10.2svdz6okz5 | MUST | search `FunctionDependency` records across all files for dependencies | SPEC-IG-QUERY-0001#s3-10:L18 |
| R.SPEC-IG-QUERY-0001.s3-10.6zowsyqbhf | MUST | If no callers exist the `callers` list — be empty. | SPEC-IG-QUERY-0001#s3-10:L20 |
| R.SPEC-IG-QUERY-0001.s3-10.sjt3edvwxc | MUST | return `{"file": file_path, "dependents": [...]}` where each entry | SPEC-IG-QUERY-0001#s3-10:L23 |
| R.SPEC-IG-QUERY-0001.s3-10.fc7o7dl5sp | MUST | use `_reverse_deps` index. If no dependents exist the list MUST be empty. | SPEC-IG-QUERY-0001#s3-10:L25 |
| R.SPEC-IG-QUERY-0001.s3-10.4sjvyphlcf | MUST | MUST use `_reverse_deps` index. If no dependents exist the list — be empty. | SPEC-IG-QUERY-0001#s3-10:L25 |
| R.SPEC-IG-QUERY-0001.s3-10.bc62t2o5jg | MUST | return `{"file": file_path, "deps": [...]}` where each entry in `deps` | SPEC-IG-QUERY-0001#s3-10:L28 |
| R.SPEC-IG-QUERY-0001.s3-10.q2bptsod54 | MUST | If no deps exist the list — be empty. | SPEC-IG-QUERY-0001#s3-10:L30 |
| R.SPEC-IG-QUERY-0001.s3-10.rebc3dnfn7 | MUST | return a dict with fields: `file` (str), `language` (str), `loc` (int), | SPEC-IG-QUERY-0001#s3-10:L33 |
| R.SPEC-IG-QUERY-0001.s3-10.kgpxxigzfd | MUST | Each symbol entry — include: `name`, `type`, `line_start`, `line_end`, | SPEC-IG-QUERY-0001#s3-10:L35 |
| R.SPEC-IG-QUERY-0001.s3-10.mnja2gwapm | MUST | If the file is not found — raise `FileNotFoundError`. | SPEC-IG-QUERY-0001#s3-10:L37 |
| R.SPEC-IG-QUERY-0001.s3-10.xp75en3ymx | MUST | return `{"query": {...}, "results": [...]}` where `query` echoes the | SPEC-IG-QUERY-0001#s3-10:L40 |
| R.SPEC-IG-QUERY-0001.s3-10.2vlsum3cga | MUST | `name_pattern` — be treated as a Python regex applied to the relative | SPEC-IG-QUERY-0001#s3-10:L43 |
| R.SPEC-IG-QUERY-0001.s3-10.t3qtkeq76n | MUST | `complexity_gt` filter — be skipped if the `FileInfo` carries no | SPEC-IG-QUERY-0001#s3-10:L45 |
| R.SPEC-IG-QUERY-0001.s3-10.hst6gr3kx5 | MUST NOT | complexity metric; files without a metric — be excluded. | SPEC-IG-QUERY-0001#s3-10:L46 |
| R.SPEC-IG-QUERY-0001.s3-10.cppwvxd6rv | MUST | `lang` — match the `language` field of `FileInfo` (case-insensitive). | SPEC-IG-QUERY-0001#s3-10:L47 |
| R.SPEC-IG-QUERY-0001.s3-10.ax4xbfzh5y | MUST | `has_symbol` — match any symbol name in the file (case-sensitive exact). | SPEC-IG-QUERY-0001#s3-10:L48 |
| R.SPEC-IG-QUERY-0001.s3-10.jmbwbneofq | MUST | All active filters — be ANDed. | SPEC-IG-QUERY-0001#s3-10:L49 |
| R.SPEC-IG-QUERY-0001.s3-10.wvzo4lsoo7 | MUST | return `{"from": file_a, "to": file_b, "path": [...], "found": bool}`. | SPEC-IG-QUERY-0001#s3-10:L52 |
| R.SPEC-IG-QUERY-0001.s3-10.ec6rwt56pl | MUST | compute the shortest directed dependency path from `file_a` to `file_b` | SPEC-IG-QUERY-0001#s3-10:L53 |
| R.SPEC-IG-QUERY-0001.s3-10.3fefleqbeq | MUST | If no path exists `found` — be `false` and `path` MUST be an empty list. | SPEC-IG-QUERY-0001#s3-10:L55 |
| R.SPEC-IG-QUERY-0001.s3-10.bqq6nhmkjo | MUST | If no path exists `found` MUST be `false` and `path` — be an empty list. | SPEC-IG-QUERY-0001#s3-10:L55 |
| R.SPEC-IG-QUERY-0001.s3-10.4ug5qjyemw | MUST | If `file_a` equals `file_b` `found` — be `true` and `path` MUST contain | SPEC-IG-QUERY-0001#s3-10:L56 |
| R.SPEC-IG-QUERY-0001.s3-10.qmix6ozgph | MUST | If `file_a` equals `file_b` `found` MUST be `true` and `path` — contain | SPEC-IG-QUERY-0001#s3-10:L56 |
| R.SPEC-IG-QUERY-0001.s3-10.kkjvqx23tn | MUST | return `{"file": file_path, "symbols": [...]}` where each symbol entry | SPEC-IG-QUERY-0001#s3-10:L60 |
| R.SPEC-IG-QUERY-0001.s3-10.mnja2gwapm~2 | MUST | If the file is not found — raise `FileNotFoundError`. | SPEC-IG-QUERY-0001#s3-10:L63 |
| R.SPEC-IG-QUERY-0001.s3-10.vywdb75c3d | MUST NOT | The module — import from `src/intentgraph/ai/`. | SPEC-IG-QUERY-0001#s3-10:L65 |
| R.SPEC-IG-QUERY-0001.s3-11.su4vsunqhp | MUST | Sub-application `query_app` — be mounted on the main `app` with name | SPEC-IG-QUERY-0001#s3-11:L5 |
| R.SPEC-IG-QUERY-0001.s3-11.eb3uufdlly | MUST | Sub-application `cache_app` — be mounted on the main `app` with name | SPEC-IG-QUERY-0001#s3-11:L7 |
| R.SPEC-IG-QUERY-0001.s3-11.tyfob4blk4 | MUST | All `query_app` commands — accept a `--repo` option of type `Path` | SPEC-IG-QUERY-0001#s3-11:L10 |
| R.SPEC-IG-QUERY-0001.s3-11.5vzyelvyxb | MUST | All `query_app` commands — : (1) call `CacheManager(repo).load_or_analyze()` | SPEC-IG-QUERY-0001#s3-11:L12 |
| R.SPEC-IG-QUERY-0001.s3-11.cafhwagxy4 | MUST | On any error, commands — print a JSON error object | SPEC-IG-QUERY-0001#s3-11:L17 |
| R.SPEC-IG-QUERY-0001.s3-11.nv3yxv4cqy | MUST | `{"error": "<message>"}` to stderr and — exit with a non-zero code. | SPEC-IG-QUERY-0001#s3-11:L18 |
| R.SPEC-IG-QUERY-0001.s3-11.rdn4s23tul | MUST | `CacheManager` — expose `load_or_analyze() -> AnalysisResult` defined as follows. | SPEC-IG-QUERY-0001#s3-11:L20 |
| R.SPEC-IG-QUERY-0001.s3-11.zza7vthzz4 | MUST | call `load()`; if `None` MUST call `RepositoryAnalyzer().analyze(repo_path)` | SPEC-IG-QUERY-0001#s3-11:L21 |
| R.SPEC-IG-QUERY-0001.s3-11.3vszkx4wph | MUST | MUST call `load()`; if `None` — call `RepositoryAnalyzer().analyze(repo_path)` | SPEC-IG-QUERY-0001#s3-11:L21 |
| R.SPEC-IG-QUERY-0001.s3-11.qgzlnkbkdb | MUST | `query_app` — expose exactly these seven sub-commands: callers, dependents, deps, context, search, path, symbols. | SPEC-IG-QUERY-0001#s3-11:L24 |
| R.SPEC-IG-QUERY-0001.s3-11.zetf4rf2yj | MUST | At least one option — be provided; if none are provided the command | SPEC-IG-QUERY-0001#s3-11:L41 |
| R.SPEC-IG-QUERY-0001.s3-11.6it64p4lfw | MUST | print a JSON error and exit non-zero. | SPEC-IG-QUERY-0001#s3-11:L42 |
| R.SPEC-IG-QUERY-0001.s3-11.uj45nsdlpw | MUST | `cache_app` — expose exactly these three sub-commands: status, warm, clear. | SPEC-IG-QUERY-0001#s3-11:L52 |
