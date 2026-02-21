"""Tests for CacheManager — T-01 of SPEC-IG-QUERY-0001."""

import hashlib
import json
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

from intentgraph.cache import CacheManager
from intentgraph.domain.models import AnalysisResult, FileInfo, Language


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _make_file_info(path: Path, content: bytes, relative_to: Path) -> FileInfo:
    """Create a FileInfo whose sha256 matches the file on disk."""
    return FileInfo(
        path=path.relative_to(relative_to),
        language=Language.PYTHON,
        sha256=_sha256(content),
        loc=1,
    )


def _make_analysis_result(root: Path, files: list[FileInfo]) -> AnalysisResult:
    return AnalysisResult(root=root, files=files)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Return a tmp directory that acts as a repo root."""
    return tmp_path


@pytest.fixture
def py_file(repo: Path) -> tuple[Path, bytes]:
    content = b"def hello(): pass\n"
    p = repo / "hello.py"
    p.write_bytes(content)
    return p, content


@pytest.fixture
def result(repo: Path, py_file: tuple[Path, bytes]) -> AnalysisResult:
    p, content = py_file
    fi = _make_file_info(p, content, repo)
    return _make_analysis_result(repo, [fi])


@pytest.fixture
def manager(repo: Path) -> CacheManager:
    return CacheManager(repo)


# ---------------------------------------------------------------------------
# Atom: class exists and accepts repo_path
# ---------------------------------------------------------------------------

class TestCacheManagerInit:
    def test_accepts_path_argument(self, repo: Path) -> None:
        mgr = CacheManager(repo)
        assert mgr is not None

    def test_cache_file_path_is_under_intentgraph_dir(self, repo: Path) -> None:
        mgr = CacheManager(repo)
        expected = repo / ".intentgraph" / "cache.json"
        assert mgr._cache_path == expected  # noqa: SLF001


# ---------------------------------------------------------------------------
# Atom: save writes atomically to the correct location
# ---------------------------------------------------------------------------

class TestSave:
    def test_save_creates_cache_file(self, manager: CacheManager, result: AnalysisResult) -> None:
        manager.save(result)
        cache_file = manager._cache_path  # noqa: SLF001
        assert cache_file.exists()

    def test_save_writes_valid_json(self, manager: CacheManager, result: AnalysisResult) -> None:
        manager.save(result)
        data = json.loads(manager._cache_path.read_text())  # noqa: SLF001
        assert isinstance(data, dict)

    def test_save_json_has_schema_version_1(self, manager: CacheManager, result: AnalysisResult) -> None:
        manager.save(result)
        data = json.loads(manager._cache_path.read_text())  # noqa: SLF001
        assert data["schema_version"] == "1"

    def test_save_json_has_result_field(self, manager: CacheManager, result: AnalysisResult) -> None:
        manager.save(result)
        data = json.loads(manager._cache_path.read_text())  # noqa: SLF001
        assert "result" in data

    def test_save_creates_parent_directory(self, repo: Path) -> None:
        mgr = CacheManager(repo)
        assert not (repo / ".intentgraph").exists()
        ar = AnalysisResult(root=repo, files=[])
        mgr.save(ar)
        assert (repo / ".intentgraph" / "cache.json").exists()

    def test_save_is_atomic_no_temp_file_left(self, manager: CacheManager, result: AnalysisResult) -> None:
        manager.save(result)
        ig_dir = manager._cache_path.parent  # noqa: SLF001
        leftover_temps = [f for f in ig_dir.iterdir() if f.name != "cache.json"]
        assert leftover_temps == []

    def test_save_uses_os_replace_for_atomic_rename(self, manager: CacheManager, result: AnalysisResult) -> None:
        from unittest.mock import patch
        import os as os_module

        original_replace = os_module.replace
        replace_calls: list[tuple[str, str]] = []

        def spy_replace(src: str, dst: str) -> None:
            replace_calls.append((src, dst))
            original_replace(src, dst)

        with patch("intentgraph.cache.os.replace", side_effect=spy_replace):
            manager.save(result)

        assert len(replace_calls) == 1, "os.replace should be called exactly once"
        assert Path(replace_calls[0][1]) == manager._cache_path  # noqa: SLF001


# ---------------------------------------------------------------------------
# Atom: load returns fresh result when cache is fresh
# ---------------------------------------------------------------------------

class TestLoadFresh:
    def test_load_returns_analysis_result_when_fresh(
        self, manager: CacheManager, result: AnalysisResult, py_file: tuple[Path, bytes]
    ) -> None:
        manager.save(result)
        loaded = manager.load()
        assert loaded is not None
        assert isinstance(loaded, AnalysisResult)

    def test_load_returns_none_when_no_cache(self, manager: CacheManager) -> None:
        loaded = manager.load()
        assert loaded is None

    def test_load_preserves_file_count(
        self, manager: CacheManager, result: AnalysisResult
    ) -> None:
        manager.save(result)
        loaded = manager.load()
        assert loaded is not None
        assert len(loaded.files) == len(result.files)


# ---------------------------------------------------------------------------
# Atom: staleness — file changed
# ---------------------------------------------------------------------------

class TestStalenessByFileChange:
    def test_load_returns_none_when_tracked_file_changed(
        self, manager: CacheManager, result: AnalysisResult, py_file: tuple[Path, bytes]
    ) -> None:
        p, _ = py_file
        manager.save(result)
        # Mutate the file on disk AFTER saving
        p.write_bytes(b"def goodbye(): pass\n")
        loaded = manager.load()
        assert loaded is None

    def test_load_returns_none_when_tracked_file_deleted(
        self, manager: CacheManager, result: AnalysisResult, py_file: tuple[Path, bytes]
    ) -> None:
        p, _ = py_file
        manager.save(result)
        p.unlink()
        loaded = manager.load()
        assert loaded is None

    def test_load_returns_result_when_sha256_unchanged(
        self, manager: CacheManager, result: AnalysisResult, py_file: tuple[Path, bytes]
    ) -> None:
        p, content = py_file
        manager.save(result)
        # Rewrite with identical content — sha256 must match
        p.write_bytes(content)
        loaded = manager.load()
        assert loaded is not None


# ---------------------------------------------------------------------------
# Atom: clear
# ---------------------------------------------------------------------------

class TestClear:
    def test_clear_deletes_cache_file(self, manager: CacheManager, result: AnalysisResult) -> None:
        manager.save(result)
        assert manager._cache_path.exists()  # noqa: SLF001
        manager.clear()
        assert not manager._cache_path.exists()  # noqa: SLF001

    def test_clear_is_idempotent_when_no_cache(self, manager: CacheManager) -> None:
        # Should not raise
        manager.clear()
        manager.clear()


# ---------------------------------------------------------------------------
# Atom: status
# ---------------------------------------------------------------------------

class TestStatus:
    def test_status_keys_present(self, manager: CacheManager) -> None:
        s = manager.status()
        assert "exists" in s
        assert "stale" in s
        assert "file_count" in s
        assert "cache_path" in s

    def test_status_exists_false_when_no_cache(self, manager: CacheManager) -> None:
        s = manager.status()
        assert s["exists"] is False

    def test_status_exists_true_after_save(
        self, manager: CacheManager, result: AnalysisResult
    ) -> None:
        manager.save(result)
        s = manager.status()
        assert s["exists"] is True

    def test_status_file_count_zero_when_no_cache(self, manager: CacheManager) -> None:
        assert manager.status()["file_count"] == 0

    def test_status_file_count_matches_saved_result(
        self, manager: CacheManager, result: AnalysisResult
    ) -> None:
        manager.save(result)
        assert manager.status()["file_count"] == len(result.files)

    def test_status_cache_path_is_string(self, manager: CacheManager) -> None:
        assert isinstance(manager.status()["cache_path"], str)

    def test_status_stale_true_when_file_changed(
        self, manager: CacheManager, result: AnalysisResult, py_file: tuple[Path, bytes]
    ) -> None:
        p, _ = py_file
        manager.save(result)
        p.write_bytes(b"# changed\n")
        assert manager.status()["stale"] is True

    def test_status_stale_false_when_fresh(
        self, manager: CacheManager, result: AnalysisResult
    ) -> None:
        manager.save(result)
        assert manager.status()["stale"] is False

    def test_status_stale_false_when_no_cache_exists(self, manager: CacheManager) -> None:
        # When cache does not exist, stale is False (nothing to be stale)
        assert manager.status()["stale"] is False


# ---------------------------------------------------------------------------
# Atom: load_or_analyze
# ---------------------------------------------------------------------------

class TestLoadOrAnalyze:
    def test_load_or_analyze_returns_cached_result_when_fresh(
        self, manager: CacheManager, result: AnalysisResult
    ) -> None:
        manager.save(result)
        returned = manager.load_or_analyze()
        assert isinstance(returned, AnalysisResult)

    def test_load_or_analyze_calls_save_when_cache_miss(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When load() returns None, load_or_analyze must call analyze then save."""
        saved: list[AnalysisResult] = []
        analyzed: list[Path] = []

        repo = tmp_path

        fake_result = AnalysisResult(root=repo, files=[])

        class FakeAnalyzer:
            def analyze(self, path: Path) -> AnalysisResult:
                analyzed.append(path)
                return fake_result

        mgr = CacheManager(repo)
        original_save = mgr.save

        def spy_save(r: AnalysisResult) -> None:
            saved.append(r)
            original_save(r)

        monkeypatch.setattr(mgr, "save", spy_save)
        monkeypatch.setattr(
            "intentgraph.cache.RepositoryAnalyzer", lambda: FakeAnalyzer()
        )

        returned = mgr.load_or_analyze()

        assert len(analyzed) == 1
        assert analyzed[0] == repo
        assert len(saved) == 1
        assert returned is fake_result

    def test_load_or_analyze_does_not_call_analyzer_when_cache_fresh(
        self, manager: CacheManager, result: AnalysisResult, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        manager.save(result)
        called: list[bool] = []

        class FakeAnalyzer:
            def analyze(self, path: Path) -> AnalysisResult:
                called.append(True)
                return result

        monkeypatch.setattr("intentgraph.cache.RepositoryAnalyzer", lambda: FakeAnalyzer())
        manager.load_or_analyze()
        assert called == []

    def test_load_or_analyze_second_call_uses_cache(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Second call to load_or_analyze() must hit the cache; analyzer called exactly once."""
        repo = tmp_path
        fake_result = AnalysisResult(root=repo, files=[])
        analyze_count: list[int] = [0]

        class FakeAnalyzer:
            def analyze(self, path: Path) -> AnalysisResult:
                analyze_count[0] += 1
                return fake_result

        mgr = CacheManager(repo)
        monkeypatch.setattr(
            "intentgraph.cache.RepositoryAnalyzer", lambda: FakeAnalyzer()
        )

        first = mgr.load_or_analyze()
        second = mgr.load_or_analyze()

        assert analyze_count[0] == 1, "analyzer must be called exactly once; second call should use the cache"
        assert first.root == second.root
        assert first.files == second.files


# ---------------------------------------------------------------------------
# Atom: no import from intentgraph.ai
# ---------------------------------------------------------------------------

class TestNoAiImport:
    def test_cache_module_does_not_import_ai(self) -> None:
        import ast
        import importlib.util
        spec = importlib.util.find_spec("intentgraph.cache")
        assert spec is not None
        source_path = Path(spec.origin)
        tree = ast.parse(source_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    assert not node.module.startswith("intentgraph.ai"), (
                        f"cache.py must not import from intentgraph.ai, found: {node.module}"
                    )
