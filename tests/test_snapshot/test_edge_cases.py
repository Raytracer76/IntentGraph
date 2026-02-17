"""Tests for edge cases and error handling."""

import json
import subprocess
from pathlib import Path

import pytest

from intentgraph.snapshot import RepoSnapshotBuilder
from intentgraph.snapshot.models import PackageManager


def _init_git_repo(repo_path: Path) -> None:
    """Initialize a directory as a git repository.

    Args:
        repo_path: Path to initialize
    """
    subprocess.run(["git", "init"], cwd=repo_path, capture_output=True, check=True)
    subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True, check=True)

    # Only commit if there are changes to commit
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=repo_path,
        capture_output=True,
    )
    if result.returncode != 0:  # Changes exist
        subprocess.run(
            ["git", "commit", "-m", "test", "--no-gpg-sign"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )


class TestEdgeCases:
    """Tests for edge cases and robustness."""

    def test_malformed_pyproject_toml(self, malformed_toml_repo: Path) -> None:
        """Malformed pyproject.toml should not crash; should emit partial runtime.

        System should gracefully handle TOML parse errors and continue.
        """
        builder = RepoSnapshotBuilder(malformed_toml_repo)

        # Should not raise exception
        snapshot = builder.build()

        # Should still analyze structure
        assert len(snapshot.structure.files) > 0, "No files analyzed"

        # Runtime detection should handle errors gracefully
        # May detect as UNKNOWN or PIP (fallback)
        assert snapshot.runtime.package_manager in [
            PackageManager.UNKNOWN,
            PackageManager.PIP,
        ], f"Unexpected package manager: {snapshot.runtime.package_manager}"

        # Python version extraction should fail gracefully (None)
        # (malformed TOML can't be parsed)
        # This is acceptable behavior

    def test_empty_directory(self, tmp_path: Path) -> None:
        """Empty directory should produce valid snapshot with no files."""
        empty_repo = tmp_path / "empty"
        empty_repo.mkdir()
        _init_git_repo(empty_repo)

        builder = RepoSnapshotBuilder(empty_repo)
        snapshot = builder.build()

        # Should have valid schema
        assert snapshot.schema_version == "1.0.0"

        # Should have no files
        assert len(snapshot.structure.files) == 0, "Expected no files"

        # Should have no languages
        assert len(snapshot.structure.languages) == 0, "Expected no languages"

        # Runtime should still be detected (even if UNKNOWN)
        assert snapshot.runtime.package_manager is not None

    def test_missing_package_json_with_nvmrc(self, tmp_path: Path) -> None:
        """Missing package.json but has .nvmrc - version extraction should work."""
        repo = tmp_path / "nvmrc_only"
        repo.mkdir()

        # Create .nvmrc
        (repo / ".nvmrc").write_text("20.10.0\n")

        # Create a simple JS file
        (repo / "index.js").write_text("console.log('hello');")

        _init_git_repo(repo)

        builder = RepoSnapshotBuilder(repo)
        snapshot = builder.build()

        # Should detect Node version from .nvmrc
        assert snapshot.runtime.node_version is not None, (
            "Node version not detected from .nvmrc alone"
        )
        assert "20.10.0" in snapshot.runtime.node_version

    def test_json_serialization_valid(self, structure_only_repo: Path) -> None:
        """Snapshot should serialize to valid JSON."""
        builder = RepoSnapshotBuilder(structure_only_repo)
        json_str = builder.build_json(indent=2)

        # Should parse as valid JSON
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON: {e}")

        # Should have required top-level keys
        assert "schema_version" in parsed
        assert "snapshot_id" in parsed
        assert "created_at" in parsed
        assert "structure" in parsed
        assert "runtime" in parsed

    def test_no_lockfile_detection(self, tmp_path: Path) -> None:
        """Repo with package.json but no lockfile should detect npm (fallback)."""
        repo = tmp_path / "no_lockfile"
        repo.mkdir()

        # Create package.json only
        (repo / "package.json").write_text('{"name": "test", "version": "1.0.0"}')
        (repo / "index.js").write_text("module.exports = {};")

        _init_git_repo(repo)

        builder = RepoSnapshotBuilder(repo)
        snapshot = builder.build()

        # Should still detect as UNKNOWN or fallback
        assert snapshot.runtime.package_manager in [
            PackageManager.UNKNOWN,
            PackageManager.NPM,
        ]

    def test_multiple_config_precedence(self, tmp_path: Path) -> None:
        """Multiple config files - should respect precedence rules."""
        repo = tmp_path / "multi_config"
        repo.mkdir()

        # Create both mypy.ini and pyproject.toml with mypy config
        (repo / "mypy.ini").write_text("[mypy]\nstrict = true\n")
        (repo / "pyproject.toml").write_text("[tool.mypy]\nstrict = false\n")
        (repo / "main.py").write_text("def main(): pass")

        _init_git_repo(repo)

        builder = RepoSnapshotBuilder(repo)
        snapshot = builder.build()

        # Should detect mypy.ini (takes precedence)
        assert snapshot.runtime.tooling.mypy is not None
        assert "mypy.ini" in snapshot.runtime.tooling.mypy, "mypy.ini not prioritized"

    def test_snapshot_size_reasonable(self, python_poetry_repo: Path) -> None:
        """Snapshot size should be reasonable for small repos."""
        builder = RepoSnapshotBuilder(python_poetry_repo)
        json_str = builder.build_json(indent=2)

        # Should be under 50KB for this small fixture
        assert len(json_str) < 50_000, f"Snapshot too large: {len(json_str)} bytes"

    def test_unicode_file_paths(self, tmp_path: Path) -> None:
        """Should handle unicode characters in file paths."""
        repo = tmp_path / "unicode_test"
        repo.mkdir()

        # Create file with unicode name
        (repo / "файл.py").write_text("# Unicode filename\ndef test(): pass")

        _init_git_repo(repo)

        builder = RepoSnapshotBuilder(repo)
        snapshot = builder.build()

        # Should include the unicode file
        file_paths = {f.path for f in snapshot.structure.files}
        assert any("файл.py" in p for p in file_paths), "Unicode filename not handled"
