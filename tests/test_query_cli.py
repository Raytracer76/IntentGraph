"""Tests for the query and cache CLI sub-command groups.

T-03 of SPEC-IG-QUERY-0001.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from intentgraph.cli import app

runner = CliRunner(mix_stderr=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_fake_result(file_count: int = 3) -> MagicMock:
    """Create a minimal fake AnalysisResult with `files` attribute."""
    result = MagicMock()
    result.files = [MagicMock() for _ in range(file_count)]
    return result


# ---------------------------------------------------------------------------
# query callers
# ---------------------------------------------------------------------------


class TestQueryCallers:
    def test_callers_success(self):
        fake_result = _make_fake_result()
        expected = {"callers": ["foo.py"]}

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch("intentgraph.query_engine.QueryEngine.callers", return_value=expected):
                result = runner.invoke(app, ["query", "callers", "my_func"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data == expected

    def test_callers_engine_error(self):
        fake_result = _make_fake_result()

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch(
                "intentgraph.query_engine.QueryEngine.callers",
                side_effect=KeyError("not found"),
            ):
                result = runner.invoke(app, ["query", "callers", "missing"])

        assert result.exit_code != 0
        data = json.loads(result.stderr)
        assert "error" in data

    def test_callers_uses_repo_option(self, tmp_path, monkeypatch):
        fake_result = _make_fake_result()
        expected = {"callers": []}

        captured = {}

        def fake_load_or_analyze(self):
            captured["repo"] = self._repo_path
            return fake_result

        with patch("intentgraph.cache.CacheManager.load_or_analyze", fake_load_or_analyze):
            with patch("intentgraph.query_engine.QueryEngine.callers", return_value=expected):
                result = runner.invoke(app, ["query", "callers", "--repo", str(tmp_path), "fn"])

        assert result.exit_code == 0
        assert captured["repo"] == tmp_path


# ---------------------------------------------------------------------------
# query dependents
# ---------------------------------------------------------------------------


class TestQueryDependents:
    def test_dependents_success(self):
        fake_result = _make_fake_result()
        expected = {"dependents": ["bar.py"]}

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch("intentgraph.query_engine.QueryEngine.dependents", return_value=expected):
                result = runner.invoke(app, ["query", "dependents", "foo.py"])

        assert result.exit_code == 0
        assert json.loads(result.stdout) == expected

    def test_dependents_error_exits_nonzero(self):
        fake_result = _make_fake_result()

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch(
                "intentgraph.query_engine.QueryEngine.dependents",
                side_effect=ValueError("oops"),
            ):
                result = runner.invoke(app, ["query", "dependents", "x.py"])

        assert result.exit_code != 0
        assert "error" in json.loads(result.stderr)


# ---------------------------------------------------------------------------
# query deps
# ---------------------------------------------------------------------------


class TestQueryDeps:
    def test_deps_success(self):
        fake_result = _make_fake_result()
        expected = {"deps": ["a.py"]}

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch("intentgraph.query_engine.QueryEngine.deps", return_value=expected):
                result = runner.invoke(app, ["query", "deps", "src/main.py"])

        assert result.exit_code == 0
        assert json.loads(result.stdout) == expected


# ---------------------------------------------------------------------------
# query context
# ---------------------------------------------------------------------------


class TestQueryContext:
    def test_context_success(self):
        fake_result = _make_fake_result()
        expected = {"context": {"loc": 100}}

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch("intentgraph.query_engine.QueryEngine.context", return_value=expected):
                result = runner.invoke(app, ["query", "context", "src/foo.py"])

        assert result.exit_code == 0
        assert json.loads(result.stdout) == expected


# ---------------------------------------------------------------------------
# query search
# ---------------------------------------------------------------------------


class TestQuerySearch:
    def test_search_no_options_exits_nonzero(self):
        fake_result = _make_fake_result()

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            result = runner.invoke(app, ["query", "search"])

        assert result.exit_code != 0
        data = json.loads(result.stderr)
        assert "error" in data

    def test_search_with_name_matches(self):
        fake_result = _make_fake_result()
        expected = {"matches": [{"path": "foo.py"}]}

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch("intentgraph.query_engine.QueryEngine.search", return_value=expected):
                result = runner.invoke(app, ["query", "search", "--name-matches", "foo"])

        assert result.exit_code == 0
        assert json.loads(result.stdout) == expected

    def test_search_with_complexity_gt(self):
        fake_result = _make_fake_result()
        expected = {"matches": []}

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch("intentgraph.query_engine.QueryEngine.search", return_value=expected):
                result = runner.invoke(app, ["query", "search", "--complexity-gt", "10"])

        assert result.exit_code == 0

    def test_search_with_lang(self):
        fake_result = _make_fake_result()
        expected = {"matches": []}

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch("intentgraph.query_engine.QueryEngine.search", return_value=expected):
                result = runner.invoke(app, ["query", "search", "--lang", "python"])

        assert result.exit_code == 0

    def test_search_with_has_symbol(self):
        fake_result = _make_fake_result()
        expected = {"matches": []}

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch("intentgraph.query_engine.QueryEngine.search", return_value=expected):
                result = runner.invoke(app, ["query", "search", "--has-symbol", "main"])

        assert result.exit_code == 0

    def test_search_with_multiple_options(self):
        fake_result = _make_fake_result()
        expected = {"matches": [{"path": "bar.py"}]}

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch("intentgraph.query_engine.QueryEngine.search", return_value=expected):
                result = runner.invoke(
                    app,
                    ["query", "search", "--name-matches", "bar", "--lang", "python"],
                )

        assert result.exit_code == 0
        assert json.loads(result.stdout) == expected

    def test_search_engine_error(self):
        fake_result = _make_fake_result()

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch(
                "intentgraph.query_engine.QueryEngine.search",
                side_effect=RuntimeError("fail"),
            ):
                result = runner.invoke(app, ["query", "search", "--name-matches", "x"])

        assert result.exit_code != 0
        assert "error" in json.loads(result.stderr)


# ---------------------------------------------------------------------------
# query path
# ---------------------------------------------------------------------------


class TestQueryPath:
    def test_path_success(self):
        fake_result = _make_fake_result()
        expected = {"path": ["a.py", "b.py"]}

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch("intentgraph.query_engine.QueryEngine.path", return_value=expected):
                result = runner.invoke(app, ["query", "path", "a.py", "b.py"])

        assert result.exit_code == 0
        assert json.loads(result.stdout) == expected

    def test_path_error_exits_nonzero(self):
        fake_result = _make_fake_result()

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch(
                "intentgraph.query_engine.QueryEngine.path",
                side_effect=KeyError("missing"),
            ):
                result = runner.invoke(app, ["query", "path", "x.py", "y.py"])

        assert result.exit_code != 0
        assert "error" in json.loads(result.stderr)


# ---------------------------------------------------------------------------
# query symbols
# ---------------------------------------------------------------------------


class TestQuerySymbols:
    def test_symbols_success(self):
        fake_result = _make_fake_result()
        expected = {"symbols": ["ClassA", "func_b"]}

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch("intentgraph.query_engine.QueryEngine.symbols", return_value=expected):
                result = runner.invoke(app, ["query", "symbols", "src/foo.py"])

        assert result.exit_code == 0
        assert json.loads(result.stdout) == expected

    def test_symbols_error_exits_nonzero(self):
        fake_result = _make_fake_result()

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            with patch(
                "intentgraph.query_engine.QueryEngine.symbols",
                side_effect=ValueError("bad path"),
            ):
                result = runner.invoke(app, ["query", "symbols", "nope.py"])

        assert result.exit_code != 0
        assert "error" in json.loads(result.stderr)


# ---------------------------------------------------------------------------
# query --repo default is Path(".")
# ---------------------------------------------------------------------------


class TestQueryRepoDefault:
    def test_default_repo_is_current_dir(self):
        fake_result = _make_fake_result()
        expected = {"callers": []}
        captured = {}

        def fake_load(self):
            captured["repo"] = self._repo_path
            return fake_result

        with patch("intentgraph.cache.CacheManager.load_or_analyze", fake_load):
            with patch("intentgraph.query_engine.QueryEngine.callers", return_value=expected):
                result = runner.invoke(app, ["query", "callers", "fn"])

        assert result.exit_code == 0
        assert captured["repo"] == Path(".")


# ---------------------------------------------------------------------------
# cache status
# ---------------------------------------------------------------------------


class TestCacheStatus:
    def test_status_success(self):
        expected = {"exists": True, "stale": False, "file_count": 5}

        with patch("intentgraph.cache.CacheManager.status", return_value=expected):
            result = runner.invoke(app, ["cache", "status"])

        assert result.exit_code == 0
        assert json.loads(result.stdout) == expected

    def test_status_with_repo_option(self, tmp_path):
        expected = {"exists": False, "stale": False, "file_count": 0}
        captured = {}

        def fake_status(self):
            captured["repo"] = self._repo_path
            return expected

        with patch("intentgraph.cache.CacheManager.status", fake_status):
            result = runner.invoke(app, ["cache", "status", "--repo", str(tmp_path)])

        assert result.exit_code == 0
        assert captured["repo"] == tmp_path

    def test_status_error_exits_nonzero(self):
        with patch("intentgraph.cache.CacheManager.status", side_effect=OSError("no")):
            result = runner.invoke(app, ["cache", "status"])

        assert result.exit_code != 0
        assert "error" in json.loads(result.stderr)


# ---------------------------------------------------------------------------
# cache warm
# ---------------------------------------------------------------------------


class TestCacheWarm:
    def test_warm_success(self):
        fake_result = _make_fake_result(file_count=7)

        with patch("intentgraph.cache.CacheManager.load_or_analyze", return_value=fake_result):
            result = runner.invoke(app, ["cache", "warm"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data == {"warmed": True, "file_count": 7}

    def test_warm_with_repo_option(self, tmp_path):
        fake_result = _make_fake_result(file_count=2)
        captured = {}

        def fake_load(self):
            captured["repo"] = self._repo_path
            return fake_result

        with patch("intentgraph.cache.CacheManager.load_or_analyze", fake_load):
            result = runner.invoke(app, ["cache", "warm", "--repo", str(tmp_path)])

        assert result.exit_code == 0
        assert captured["repo"] == tmp_path
        assert json.loads(result.stdout)["file_count"] == 2

    def test_warm_error_exits_nonzero(self):
        with patch(
            "intentgraph.cache.CacheManager.load_or_analyze",
            side_effect=RuntimeError("disk full"),
        ):
            result = runner.invoke(app, ["cache", "warm"])

        assert result.exit_code != 0
        assert "error" in json.loads(result.stderr)


# ---------------------------------------------------------------------------
# cache clear
# ---------------------------------------------------------------------------


class TestCacheClear:
    def test_clear_success(self):
        with patch("intentgraph.cache.CacheManager.clear", return_value=None):
            result = runner.invoke(app, ["cache", "clear"])

        assert result.exit_code == 0
        assert json.loads(result.stdout) == {"cleared": True}

    def test_clear_with_repo_option(self, tmp_path):
        captured = {}

        def fake_clear(self):
            captured["repo"] = self._repo_path

        with patch("intentgraph.cache.CacheManager.clear", fake_clear):
            result = runner.invoke(app, ["cache", "clear", "--repo", str(tmp_path)])

        assert result.exit_code == 0
        assert captured["repo"] == tmp_path

    def test_clear_error_exits_nonzero(self):
        with patch(
            "intentgraph.cache.CacheManager.clear",
            side_effect=PermissionError("denied"),
        ):
            result = runner.invoke(app, ["cache", "clear"])

        assert result.exit_code != 0
        assert "error" in json.loads(result.stderr)


# ---------------------------------------------------------------------------
# Help text smoke tests
# ---------------------------------------------------------------------------


class TestHelpText:
    def test_query_help_lists_subcommands(self):
        result = runner.invoke(app, ["query", "--help"])
        assert result.exit_code == 0
        for cmd in ("callers", "dependents", "deps", "context", "search", "path", "symbols"):
            assert cmd in result.stdout

    def test_cache_help_lists_subcommands(self):
        result = runner.invoke(app, ["cache", "--help"])
        assert result.exit_code == 0
        for cmd in ("status", "warm", "clear"):
            assert cmd in result.stdout
