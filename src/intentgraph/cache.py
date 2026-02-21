"""CacheManager — disk-backed cache for AnalysisResult with SHA-256 staleness detection.

SPEC-IG-QUERY-0001, T-01.
"""

import hashlib
import json
import os
import tempfile
from pathlib import Path

from .application.analyzer import RepositoryAnalyzer
from .domain.models import AnalysisResult

_SCHEMA_VERSION = "1"


class CacheManager:
    """Persist an :class:`AnalysisResult` to disk and detect when it becomes stale.

    The cache file lives at ``<repo_path>/.intentgraph/cache.json``.
    Staleness is determined by comparing the SHA-256 digest stored in each
    :class:`~intentgraph.domain.models.FileInfo` against the current digest of
    the corresponding file on disk.

    Args:
        repo_path: Absolute path to the root of the repository being analysed.
    """

    def __init__(self, repo_path: Path) -> None:
        self._repo_path: Path = repo_path
        self._cache_path: Path = repo_path / ".intentgraph" / "cache.json"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> AnalysisResult | None:
        """Return the cached :class:`AnalysisResult` if it is fresh, otherwise ``None``.

        Returns ``None`` when:
        - the cache file does not exist, or
        - the schema_version is unknown, or
        - any tracked file has a different SHA-256 digest on disk, or
        - any tracked file no longer exists on disk.
        """
        if not self._cache_path.exists():
            return None

        try:
            data = json.loads(self._cache_path.read_text(encoding="utf-8"))
            if data.get("schema_version") != "1":
                return None
            result = AnalysisResult.model_validate(data["result"])
        except Exception:
            return None

        if self._is_stale(result):
            return None

        return result

    def save(self, result: AnalysisResult) -> None:
        """Persist *result* to the cache file atomically.

        The parent directory is created if it does not exist.
        The write is performed via a temp-file + rename to avoid partially
        written cache files (atomic write guarantee).

        Args:
            result: The analysis result to cache.
        """
        cache_dir = self._cache_path.parent
        cache_dir.mkdir(parents=True, exist_ok=True)

        payload = {
            "schema_version": _SCHEMA_VERSION,
            "result": result.model_dump(mode="json"),
        }
        serialised = json.dumps(payload, indent=2)

        # Write to a sibling temp file then rename — atomic on POSIX.
        fd, tmp_path = tempfile.mkstemp(dir=cache_dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(serialised)
            os.replace(tmp_path, self._cache_path)
        except Exception:
            # Clean up the temp file if rename failed.
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def clear(self) -> None:
        """Delete the cache file if it exists.

        Calling this method when no cache file is present is a no-op.
        """
        try:
            self._cache_path.unlink()
        except FileNotFoundError:
            pass

    def status(self) -> dict[str, bool | int | str]:
        """Return a summary dict describing the current cache state.

        Returns:
            A dict with keys:

            ``exists`` (:class:`bool`)
                Whether the cache file exists.
            ``stale`` (:class:`bool`)
                Whether the cache is stale.  ``False`` when the cache does not
                exist (there is nothing to be stale).
            ``file_count`` (:class:`int`)
                Number of tracked files in the cache, or ``0`` if no cache.
            ``cache_path`` (:class:`str`)
                Absolute path to the cache file as a string.
        """
        exists = self._cache_path.exists()
        stale = False
        file_count = 0

        if exists:
            try:
                data = json.loads(self._cache_path.read_text(encoding="utf-8"))
                if data.get("schema_version") != _SCHEMA_VERSION:
                    stale = True
                else:
                    result = AnalysisResult.model_validate(data["result"])
                    file_count = len(result.files)
                    stale = self._is_stale(result)
            except Exception:
                stale = True

        return {
            "exists": exists,
            "stale": stale,
            "file_count": file_count,
            "cache_path": str(self._cache_path),
        }

    def load_or_analyze(self) -> AnalysisResult:
        """Return a fresh :class:`AnalysisResult`, using the cache when possible.

        If :meth:`load` returns a valid (non-stale) result, that is returned
        immediately.  Otherwise the repository is analysed via
        :class:`~intentgraph.application.analyzer.RepositoryAnalyzer`, the
        result is saved to the cache, and then returned.

        Returns:
            An :class:`AnalysisResult` for :attr:`_repo_path`.
        """
        cached = self.load()
        if cached is not None:
            return cached

        analyzer = RepositoryAnalyzer()
        result = analyzer.analyze(self._repo_path)
        self.save(result)
        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _is_stale(self, result: AnalysisResult) -> bool:
        """Return ``True`` if any tracked file has changed or is missing."""
        for file_info in result.files:
            full_path = self._repo_path / file_info.path
            if not full_path.exists():
                return True
            current_digest = hashlib.sha256(full_path.read_bytes()).hexdigest()
            if current_digest != file_info.sha256:
                return True
        return False
