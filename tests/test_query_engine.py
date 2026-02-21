"""Tests for QueryEngine — T-02 of SPEC-IG-QUERY-0001."""

import json
import re
from pathlib import Path
from uuid import uuid4

import pytest

from intentgraph.domain.models import (
    AnalysisResult,
    APIExport,
    CodeSymbol,
    FileInfo,
    FunctionDependency,
    Language,
)
from intentgraph.query_engine import QueryEngine


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _make_symbol(name: str, symbol_type: str = "function", line_start: int = 1,
                 line_end: int = 5, signature: str = None,
                 is_exported: bool = False, is_private: bool = False) -> CodeSymbol:
    return CodeSymbol(
        name=name,
        symbol_type=symbol_type,
        line_start=line_start,
        line_end=line_end,
        signature=signature,
        is_exported=is_exported,
        is_private=is_private,
    )


def _make_export(name: str, export_type: str = "function") -> APIExport:
    return APIExport(name=name, export_type=export_type)


def _make_file(path_str: str, language: Language = Language.PYTHON,
               symbols=None, exports=None, function_dependencies=None,
               dependencies=None, loc: int = 10) -> FileInfo:
    return FileInfo(
        path=Path(path_str),
        language=language,
        sha256="abc123",
        loc=loc,
        symbols=symbols or [],
        exports=exports or [],
        function_dependencies=function_dependencies or [],
        dependencies=dependencies or [],
    )


def _make_result(files: list[FileInfo]) -> AnalysisResult:
    return AnalysisResult(root=Path("/repo"), files=files)


def _is_json_serialisable(obj) -> bool:
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Fixture: a standard multi-file result for reuse
# ---------------------------------------------------------------------------

@pytest.fixture
def sym_foo():
    return _make_symbol("foo", "function", 1, 5, "def foo(): ...", is_exported=True)

@pytest.fixture
def sym_bar():
    return _make_symbol("bar", "function", 10, 15, signature=None, is_private=True)

@pytest.fixture
def sym_Baz():
    return _make_symbol("Baz", "class", 1, 20, "class Baz:", is_exported=True)

@pytest.fixture
def file_a(sym_foo, sym_bar):
    return _make_file("src/a.py", symbols=[sym_foo, sym_bar],
                      exports=[_make_export("foo")], loc=20)

@pytest.fixture
def file_b(sym_Baz):
    return _make_file("src/b.py", language=Language.PYTHON,
                      symbols=[sym_Baz], exports=[_make_export("Baz", "class")], loc=30)

@pytest.fixture
def file_js():
    return _make_file("src/c.js", language=Language.JAVASCRIPT, loc=5)

@pytest.fixture
def result_with_deps(sym_foo, sym_bar, sym_Baz):
    """
    a.py depends on b.py (file-level)
    b.py has no file-level deps
    There's also a FunctionDependency: bar in a.py calls Baz in b.py
    """
    file_b = _make_file("src/b.py", language=Language.PYTHON,
                        symbols=[sym_Baz], exports=[_make_export("Baz", "class")], loc=30)
    # Build a FunctionDependency: bar -> Baz
    fd = FunctionDependency(
        from_symbol=sym_bar.id,
        to_symbol=sym_Baz.id,
        to_file=file_b.id,
        dependency_type="calls",
        line_number=12,
        context="baz_instance = Baz()",
    )
    file_a = _make_file("src/a.py", symbols=[sym_foo, sym_bar],
                        exports=[_make_export("foo")], loc=20,
                        function_dependencies=[fd],
                        dependencies=[file_b.id])
    return _make_result([file_a, file_b])


@pytest.fixture
def engine_with_deps(result_with_deps):
    return QueryEngine(result_with_deps)


# ---------------------------------------------------------------------------
# Construction / index tests
# ---------------------------------------------------------------------------

class TestConstruction:
    def test_constructs_from_analysis_result(self, result_with_deps):
        engine = QueryEngine(result_with_deps)
        assert engine is not None

    def test_file_by_id_index(self, result_with_deps):
        engine = QueryEngine(result_with_deps)
        for fi in result_with_deps.files:
            assert fi.id in engine._file_by_id
            assert engine._file_by_id[fi.id] is fi

    def test_file_by_path_index(self, result_with_deps):
        engine = QueryEngine(result_with_deps)
        for fi in result_with_deps.files:
            key = str(fi.path)
            assert key in engine._file_by_path
            assert engine._file_by_path[key] is fi

    def test_symbol_by_name_index(self, result_with_deps):
        engine = QueryEngine(result_with_deps)
        assert "foo" in engine._symbol_by_name
        assert "bar" in engine._symbol_by_name
        assert "Baz" in engine._symbol_by_name
        # Each entry is a list of (FileInfo, CodeSymbol)
        entry = engine._symbol_by_name["foo"][0]
        assert len(entry) == 2
        fi, sym = entry
        assert isinstance(fi, FileInfo)
        assert isinstance(sym, CodeSymbol)

    def test_reverse_deps_index(self, result_with_deps):
        engine = QueryEngine(result_with_deps)
        # file_a depends on file_b, so file_b.id -> [file_a.id]
        file_a = result_with_deps.files[0]
        file_b = result_with_deps.files[1]
        assert file_b.id in engine._reverse_deps
        assert file_a.id in engine._reverse_deps[file_b.id]

    def test_reverse_deps_empty_for_leaf(self, result_with_deps):
        engine = QueryEngine(result_with_deps)
        file_a = result_with_deps.files[0]
        # file_a is not depended upon by anything
        assert file_a.id not in engine._reverse_deps or \
               engine._reverse_deps.get(file_a.id, []) == []

    def test_empty_result(self):
        result = _make_result([])
        engine = QueryEngine(result)
        assert engine._file_by_id == {}
        assert engine._file_by_path == {}
        assert engine._symbol_by_name == {}
        assert engine._reverse_deps == {}


# ---------------------------------------------------------------------------
# callers()
# ---------------------------------------------------------------------------

class TestCallers:
    def test_returns_callers_dict_structure(self, engine_with_deps):
        result = engine_with_deps.callers("Baz")
        assert result["symbol"] == "Baz"
        assert "callers" in result
        assert isinstance(result["callers"], list)

    def test_finds_caller(self, engine_with_deps):
        result = engine_with_deps.callers("Baz")
        assert len(result["callers"]) == 1
        entry = result["callers"][0]
        assert entry["file"] == "src/a.py"
        assert entry["line"] == 12
        assert entry["context"] == "baz_instance = Baz()"

    def test_no_callers_returns_empty_list(self, engine_with_deps):
        result = engine_with_deps.callers("foo")
        assert result["callers"] == []

    def test_unknown_symbol_returns_empty_list(self, engine_with_deps):
        result = engine_with_deps.callers("nonexistent")
        assert result["callers"] == []

    def test_case_sensitive_match(self, engine_with_deps):
        result = engine_with_deps.callers("baz")  # lowercase
        assert result["callers"] == []

    def test_json_serialisable(self, engine_with_deps):
        result = engine_with_deps.callers("Baz")
        assert _is_json_serialisable(result)

    def test_context_none_when_not_provided(self):
        sym_target = _make_symbol("target")
        fd = FunctionDependency(
            from_symbol=uuid4(),
            to_symbol=sym_target.id,
            to_file=uuid4(),
            dependency_type="calls",
            line_number=5,
            context=None,
        )
        caller_file = _make_file("caller.py", function_dependencies=[fd])
        target_file = _make_file("target.py", symbols=[sym_target])
        engine = QueryEngine(_make_result([caller_file, target_file]))
        result = engine.callers("target")
        assert len(result["callers"]) == 1
        assert result["callers"][0]["context"] is None


# ---------------------------------------------------------------------------
# dependents()
# ---------------------------------------------------------------------------

class TestDependents:
    def test_returns_dependents_structure(self, engine_with_deps):
        # file_b has file_a as a dependent
        result = engine_with_deps.dependents("src/b.py")
        assert result["file"] == "src/b.py"
        assert "dependents" in result
        assert isinstance(result["dependents"], list)

    def test_finds_dependent(self, engine_with_deps):
        result = engine_with_deps.dependents("src/b.py")
        assert len(result["dependents"]) == 1
        entry = result["dependents"][0]
        assert entry["file"] == "src/a.py"
        assert "dependency_type" in entry

    def test_no_dependents_returns_empty(self, engine_with_deps):
        result = engine_with_deps.dependents("src/a.py")
        assert result["dependents"] == []

    def test_unknown_file_returns_empty(self, engine_with_deps):
        result = engine_with_deps.dependents("does_not_exist.py")
        assert result["dependents"] == []

    def test_json_serialisable(self, engine_with_deps):
        result = engine_with_deps.dependents("src/b.py")
        assert _is_json_serialisable(result)


# ---------------------------------------------------------------------------
# deps()
# ---------------------------------------------------------------------------

class TestDeps:
    def test_returns_deps_structure(self, engine_with_deps):
        result = engine_with_deps.deps("src/a.py")
        assert result["file"] == "src/a.py"
        assert "deps" in result
        assert isinstance(result["deps"], list)

    def test_finds_dep(self, engine_with_deps):
        result = engine_with_deps.deps("src/a.py")
        assert len(result["deps"]) == 1
        entry = result["deps"][0]
        assert entry["file"] == "src/b.py"
        assert "dependency_type" in entry

    def test_no_deps_returns_empty(self, engine_with_deps):
        result = engine_with_deps.deps("src/b.py")
        assert result["deps"] == []

    def test_unknown_file_returns_empty(self, engine_with_deps):
        result = engine_with_deps.deps("nope.py")
        assert result["deps"] == []

    def test_json_serialisable(self, engine_with_deps):
        result = engine_with_deps.deps("src/a.py")
        assert _is_json_serialisable(result)

    def test_dependency_type_field(self, engine_with_deps):
        result = engine_with_deps.deps("src/a.py")
        assert result["deps"][0]["dependency_type"] == "file-level"


# ---------------------------------------------------------------------------
# context()
# ---------------------------------------------------------------------------

class TestContext:
    def test_returns_full_context(self, engine_with_deps):
        result = engine_with_deps.context("src/a.py")
        assert result["file"] == "src/a.py"
        assert result["language"] == "python"
        assert isinstance(result["loc"], int)
        assert isinstance(result["sha256"], str)
        assert isinstance(result["symbols"], list)
        assert isinstance(result["exports"], list)
        assert isinstance(result["deps"], list)
        assert isinstance(result["dependents"], list)

    def test_symbols_have_required_fields(self, engine_with_deps):
        result = engine_with_deps.context("src/a.py")
        for sym in result["symbols"]:
            assert "name" in sym
            assert "type" in sym
            assert "line_start" in sym
            assert "line_end" in sym
            assert "signature" in sym
            assert "is_exported" in sym
            assert "is_private" in sym

    def test_signature_can_be_null(self, engine_with_deps):
        result = engine_with_deps.context("src/a.py")
        # sym_bar has no signature
        bar_entries = [s for s in result["symbols"] if s["name"] == "bar"]
        assert len(bar_entries) == 1
        assert bar_entries[0]["signature"] is None

    def test_file_not_found_raises(self, engine_with_deps):
        with pytest.raises(FileNotFoundError):
            engine_with_deps.context("nonexistent.py")

    def test_json_serialisable(self, engine_with_deps):
        result = engine_with_deps.context("src/a.py")
        assert _is_json_serialisable(result)

    def test_language_is_string(self, engine_with_deps):
        result = engine_with_deps.context("src/b.py")
        assert isinstance(result["language"], str)

    def test_exports_included(self, engine_with_deps):
        result = engine_with_deps.context("src/a.py")
        assert len(result["exports"]) >= 1


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------

class TestSearch:
    def test_no_filters_returns_all(self, engine_with_deps):
        result = engine_with_deps.search()
        assert "query" in result
        assert "results" in result
        assert len(result["results"]) == 2

    def test_query_echoes_filters(self, engine_with_deps):
        result = engine_with_deps.search(lang="python")
        assert result["query"]["lang"] == "python"

    def test_lang_filter_case_insensitive(self, engine_with_deps):
        result = engine_with_deps.search(lang="Python")
        assert len(result["results"]) == 2

    def test_lang_filter_js(self):
        file_py = _make_file("a.py", language=Language.PYTHON)
        file_js = _make_file("b.js", language=Language.JAVASCRIPT)
        engine = QueryEngine(_make_result([file_py, file_js]))
        result = engine.search(lang="javascript")
        assert len(result["results"]) == 1
        assert result["results"][0]["file"] == "b.js"

    def test_name_pattern_filter(self, engine_with_deps):
        result = engine_with_deps.search(name_pattern=r"a\.py$")
        assert len(result["results"]) == 1
        assert result["results"][0]["file"] == "src/a.py"

    def test_name_pattern_none_all_pass(self, engine_with_deps):
        result = engine_with_deps.search(name_pattern=None)
        assert len(result["results"]) == 2

    def test_has_symbol_filter(self, engine_with_deps):
        result = engine_with_deps.search(has_symbol="Baz")
        assert len(result["results"]) == 1
        assert result["results"][0]["file"] == "src/b.py"

    def test_has_symbol_case_sensitive(self, engine_with_deps):
        result = engine_with_deps.search(has_symbol="baz")
        assert len(result["results"]) == 0

    def test_and_combining_filters(self, engine_with_deps):
        result = engine_with_deps.search(lang="python", has_symbol="Baz")
        assert len(result["results"]) == 1

    def test_result_fields(self, engine_with_deps):
        result = engine_with_deps.search()
        for entry in result["results"]:
            assert "file" in entry
            assert "language" in entry
            assert "loc" in entry
            assert "symbol_count" in entry

    def test_complexity_gt_skipped_when_no_metric(self, engine_with_deps):
        # Files have no complexity attribute on symbols, so filter is skipped
        result = engine_with_deps.search(complexity_gt=1000)
        assert len(result["results"]) == 2

    def test_complexity_gt_filters_when_metric_present(self):
        # Use complexity_score on FileInfo as proxy (see note in spec)
        sym_hi = _make_symbol("complex_fn")
        # Attach a fake complexity attribute
        object.__setattr__(sym_hi, 'complexity', 50) if False else None
        # Instead test via a FileInfo with complexity_score
        file_hi = FileInfo(
            path=Path("hi.py"), language=Language.PYTHON,
            sha256="x", loc=100, complexity_score=50,
        )
        file_lo = FileInfo(
            path=Path("lo.py"), language=Language.PYTHON,
            sha256="y", loc=10, complexity_score=5,
        )
        engine = QueryEngine(_make_result([file_hi, file_lo]))
        # complexity_gt checks FileInfo.complexity_score when present
        result = engine.search(complexity_gt=20)
        files_returned = {r["file"] for r in result["results"]}
        # hi.py has complexity_score=50 > 20, lo.py has 5 which is not > 20
        # But per spec: "files without a metric MUST NOT be excluded"
        # Both files HAVE complexity_score (0 is not "no metric" — score=0 means no info)
        # Actually: complexity_score=0 (default) means "no metric" per our interpretation
        # lo.py complexity_score=5 > 0, hi.py complexity_score=50 > 0
        # So both have metrics; hi.py passes (50>20), lo.py fails (5 not >20)
        assert "hi.py" in files_returned
        assert "lo.py" not in files_returned

    def test_complexity_gt_files_with_zero_score_not_excluded(self):
        file_zero = FileInfo(
            path=Path("zero.py"), language=Language.PYTHON,
            sha256="z", loc=10, complexity_score=0,
        )
        engine = QueryEngine(_make_result([file_zero]))
        result = engine.search(complexity_gt=5)
        # complexity_score=0 means no metric => file is NOT excluded
        assert len(result["results"]) == 1

    def test_json_serialisable(self, engine_with_deps):
        result = engine_with_deps.search(lang="python", has_symbol="foo")
        assert _is_json_serialisable(result)


# ---------------------------------------------------------------------------
# path()
# ---------------------------------------------------------------------------

class TestPath:
    def test_same_file_returns_single_entry(self, engine_with_deps):
        result = engine_with_deps.path("src/a.py", "src/a.py")
        assert result["found"] is True
        assert result["path"] == ["src/a.py"]

    def test_direct_dependency_found(self, engine_with_deps):
        result = engine_with_deps.path("src/a.py", "src/b.py")
        assert result["found"] is True
        assert result["path"] == ["src/a.py", "src/b.py"]

    def test_no_path_returns_false(self, engine_with_deps):
        # b.py does not depend on a.py
        result = engine_with_deps.path("src/b.py", "src/a.py")
        assert result["found"] is False
        assert result["path"] == []

    def test_returns_correct_structure(self, engine_with_deps):
        result = engine_with_deps.path("src/a.py", "src/b.py")
        assert "from" in result
        assert "to" in result
        assert "path" in result
        assert "found" in result
        assert result["from"] == "src/a.py"
        assert result["to"] == "src/b.py"

    def test_unknown_file_a_returns_not_found(self, engine_with_deps):
        result = engine_with_deps.path("unknown.py", "src/b.py")
        assert result["found"] is False
        assert result["path"] == []

    def test_unknown_file_b_returns_not_found(self, engine_with_deps):
        result = engine_with_deps.path("src/a.py", "unknown.py")
        assert result["found"] is False
        assert result["path"] == []

    def test_multi_hop_path(self):
        """a -> b -> c: path("a.py","c.py") should be ["a.py","b.py","c.py"]"""
        file_c = _make_file("c.py")
        file_b = _make_file("b.py", dependencies=[file_c.id])
        file_a = _make_file("a.py", dependencies=[file_b.id])
        engine = QueryEngine(_make_result([file_a, file_b, file_c]))
        result = engine.path("a.py", "c.py")
        assert result["found"] is True
        assert result["path"] == ["a.py", "b.py", "c.py"]

    def test_json_serialisable(self, engine_with_deps):
        result = engine_with_deps.path("src/a.py", "src/b.py")
        assert _is_json_serialisable(result)


    def test_path_same_file_not_in_index_still_returns_found_true(self, engine_with_deps):
        result = engine_with_deps.path("not_in_graph.py", "not_in_graph.py")
        assert result["found"] is True
        assert result["path"] == ["not_in_graph.py"]


# ---------------------------------------------------------------------------
# symbols()
# ---------------------------------------------------------------------------

class TestSymbols:
    def test_returns_symbols_structure(self, engine_with_deps):
        result = engine_with_deps.symbols("src/a.py")
        assert result["file"] == "src/a.py"
        assert "symbols" in result
        assert isinstance(result["symbols"], list)

    def test_returns_all_symbols(self, engine_with_deps):
        result = engine_with_deps.symbols("src/a.py")
        names = {s["name"] for s in result["symbols"]}
        assert "foo" in names
        assert "bar" in names

    def test_symbol_fields(self, engine_with_deps):
        result = engine_with_deps.symbols("src/a.py")
        for sym in result["symbols"]:
            assert "name" in sym
            assert "type" in sym
            assert "line_start" in sym
            assert "line_end" in sym
            assert "signature" in sym
            assert "is_exported" in sym
            assert "is_private" in sym

    def test_file_not_found_raises(self, engine_with_deps):
        with pytest.raises(FileNotFoundError):
            engine_with_deps.symbols("nonexistent.py")

    def test_empty_file_returns_empty_list(self):
        fi = _make_file("empty.py")
        engine = QueryEngine(_make_result([fi]))
        result = engine.symbols("empty.py")
        assert result["symbols"] == []

    def test_json_serialisable(self, engine_with_deps):
        result = engine_with_deps.symbols("src/a.py")
        assert _is_json_serialisable(result)

    def test_is_exported_values(self, engine_with_deps):
        result = engine_with_deps.symbols("src/a.py")
        foo_entry = next(s for s in result["symbols"] if s["name"] == "foo")
        bar_entry = next(s for s in result["symbols"] if s["name"] == "bar")
        assert foo_entry["is_exported"] is True
        assert bar_entry["is_private"] is True


# ---------------------------------------------------------------------------
# No import from intentgraph.ai
# ---------------------------------------------------------------------------

class TestNoAIImport:
    def test_no_ai_import(self):
        import importlib
        import importlib.util
        spec = importlib.util.find_spec("intentgraph.query_engine")
        assert spec is not None
        # Check that no import statement imports from intentgraph.ai
        source_path = spec.origin
        with open(source_path) as f:
            lines = f.readlines()
        import_lines = [
            ln.strip() for ln in lines
            if ln.strip().startswith(("import ", "from "))
        ]
        for line in import_lines:
            assert "intentgraph.ai" not in line, (
                f"query_engine must not import from intentgraph.ai, found: {line!r}"
            )
