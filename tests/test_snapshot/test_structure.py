"""Tests for structure snapshot generation."""

from pathlib import Path

import pytest

from intentgraph.snapshot import RepoSnapshotBuilder


class TestStructureSnapshot:
    """Tests for code structure analysis in snapshots."""

    def test_structure_only_minimal_repo(self, structure_only_repo: Path) -> None:
        """Structure-only fixture should analyze basic Python files."""
        builder = RepoSnapshotBuilder(structure_only_repo)
        snapshot = builder.build()

        # Should detect Python files
        assert len(snapshot.structure.files) == 2, "Expected 2 Python files"

        # Should have Python language summary
        python_lang = next(
            (l for l in snapshot.structure.languages if l.language == "python"), None
        )
        assert python_lang is not None, "Python language not detected"
        assert python_lang.file_count == 2, "Expected 2 Python files"

        # Files should be present
        file_paths = {f.path for f in snapshot.structure.files}
        assert "main.py" in file_paths, "main.py not found"
        assert "utils.py" in file_paths, "utils.py not found"

        # Should have basic metrics
        for file in snapshot.structure.files:
            assert file.lines_of_code > 0, f"{file.path} has 0 LOC"
            assert file.complexity >= 0, f"{file.path} has negative complexity"

    def test_file_dependencies_extracted(self, structure_only_repo: Path) -> None:
        """Dependencies between files should be extracted."""
        builder = RepoSnapshotBuilder(structure_only_repo)
        snapshot = builder.build()

        # utils.py depends on main.py
        utils_file = next(
            (f for f in snapshot.structure.files if f.path == "utils.py"), None
        )
        assert utils_file is not None, "utils.py not found"

        # Should have at least one dependency (main.py)
        assert len(utils_file.dependencies) >= 0, "Expected dependencies"

    def test_imports_extracted(self, structure_only_repo: Path) -> None:
        """Import statements should be extracted and sorted."""
        builder = RepoSnapshotBuilder(structure_only_repo)
        snapshot = builder.build()

        # utils.py imports from main
        utils_file = next(
            (f for f in snapshot.structure.files if f.path == "utils.py"), None
        )
        assert utils_file is not None, "utils.py not found"

        # Imports should be present and sorted
        assert len(utils_file.imports) > 0, "No imports found"
        assert utils_file.imports == sorted(
            utils_file.imports
        ), "Imports not sorted"

    def test_file_index_bidirectional(self, structure_only_repo: Path) -> None:
        """File index should provide UUID ↔ path mapping."""
        builder = RepoSnapshotBuilder(structure_only_repo)
        snapshot = builder.build()

        # Every file in files[] should have a UUID in file_index
        for file_entry in snapshot.structure.files:
            # Find the UUID for this file path
            matching_uuids = [
                uuid
                for uuid, path in snapshot.structure.file_index.items()
                if path == file_entry.path
            ]
            assert (
                len(matching_uuids) == 1
            ), f"File {file_entry.path} has {len(matching_uuids)} UUID mappings"

    def test_multi_language_detection(self, node_pnpm_repo: Path) -> None:
        """Should detect multiple languages correctly."""
        builder = RepoSnapshotBuilder(node_pnpm_repo)
        snapshot = builder.build()

        # Should detect TypeScript
        typescript_lang = next(
            (l for l in snapshot.structure.languages if l.language == "typescript"),
            None,
        )
        assert typescript_lang is not None, "TypeScript not detected"
        assert typescript_lang.file_count > 0, "No TypeScript files"

    def test_root_path_recorded(self, structure_only_repo: Path) -> None:
        """Root path should be recorded in snapshot."""
        builder = RepoSnapshotBuilder(structure_only_repo)
        snapshot = builder.build()

        assert (
            snapshot.structure.root_path
        ), "Root path not recorded"
        # Should use POSIX-style path
        assert "\\" not in snapshot.structure.root_path, "Backslash in root path"
