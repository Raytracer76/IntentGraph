"""Tests for deterministic snapshot generation."""

import json
from pathlib import Path

import pytest

from intentgraph.snapshot import RepoSnapshotBuilder

from .conftest import strip_timestamps


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_idempotence_same_run(self, structure_only_repo: Path) -> None:
        """Generate snapshot twice in same run → identical bytes (excluding timestamp).

        This is the key determinism test: same input = same output.
        """
        builder = RepoSnapshotBuilder(structure_only_repo)

        # Generate twice
        json1 = builder.build_json(indent=2)
        json2 = builder.build_json(indent=2)

        # Parse and strip timestamps
        data1 = strip_timestamps(json.loads(json1))
        data2 = strip_timestamps(json.loads(json2))

        # Should be identical
        assert data1 == data2, "Snapshots differ across multiple generations"

    def test_uuid_stability(self, structure_only_repo: Path) -> None:
        """UUIDs should be stable for the same file paths."""
        builder = RepoSnapshotBuilder(structure_only_repo)

        # Generate snapshot twice
        snapshot1 = builder.build()
        snapshot2 = builder.build()

        # Extract file UUIDs
        uuids1 = set(snapshot1.structure.file_index.keys())
        uuids2 = set(snapshot2.structure.file_index.keys())

        # UUIDs should be identical
        assert uuids1 == uuids2, "File UUIDs differ across generations"

        # Verify UUID → path mapping is identical
        assert snapshot1.structure.file_index == snapshot2.structure.file_index, (
            "UUID → path mapping differs"
        )

    def test_ordering_stability(self, python_poetry_repo: Path) -> None:
        """Arrays should maintain stable ordering."""
        builder = RepoSnapshotBuilder(python_poetry_repo)

        snapshot = builder.build()

        # Languages should be sorted
        languages = [lang.language for lang in snapshot.structure.languages]
        assert languages == sorted(languages), "Languages not sorted"

        # Files should be sorted by path
        files = [f.path for f in snapshot.structure.files]
        assert files == sorted(files), "Files not sorted by path"

        # File index should be sorted by UUID
        file_index_keys = list(snapshot.structure.file_index.keys())
        assert file_index_keys == sorted(file_index_keys), (
            "File index not sorted by UUID"
        )

        # Dependencies within each file should be sorted
        for file_entry in snapshot.structure.files:
            assert file_entry.dependencies == sorted(file_entry.dependencies), (
                f"Dependencies not sorted for {file_entry.path}"
            )

        # Imports within each file should be sorted
        for file_entry in snapshot.structure.files:
            assert file_entry.imports == sorted(file_entry.imports), (
                f"Imports not sorted for {file_entry.path}"
            )

    def test_cross_platform_uuid_consistency(self, structure_only_repo: Path) -> None:
        """UUIDs should use POSIX-style paths regardless of platform.

        This verifies the Path.as_posix() normalization works.
        """
        builder = RepoSnapshotBuilder(structure_only_repo)
        snapshot = builder.build()

        # Verify file_index uses only forward slashes in paths
        for uuid, file_path in snapshot.structure.file_index.items():
            assert "\\" not in file_path, f"Backslash found in path: {file_path}"
            assert "/" in file_path or "." in file_path, f"Invalid path: {file_path}"

    def test_schema_version_stable(self, structure_only_repo: Path) -> None:
        """Schema version should be 1.0.0 for all snapshots."""
        builder = RepoSnapshotBuilder(structure_only_repo)
        snapshot = builder.build()

        assert snapshot.schema_version == "1.0.0", (
            f"Expected schema_version 1.0.0, got {snapshot.schema_version}"
        )

    @pytest.mark.parametrize(
        "fixture_name",
        [
            "structure_only_repo",
            "node_pnpm_repo",
            "python_poetry_repo",
            "mixed_tooling_repo",
        ],
    )
    def test_determinism_across_fixtures(
        self, fixture_name: str, request: pytest.FixtureRequest
    ) -> None:
        """All fixture repos should produce deterministic output."""
        repo_path = request.getfixturevalue(fixture_name)
        builder = RepoSnapshotBuilder(repo_path)

        # Generate multiple times
        snapshots = [builder.build() for _ in range(3)]

        # Strip timestamps and compare
        json_outputs = [
            json.dumps(
                strip_timestamps(json.loads(s.model_dump_json())), sort_keys=True
            )
            for s in snapshots
        ]

        # All should be identical
        assert len(set(json_outputs)) == 1, (
            f"Non-deterministic output for {fixture_name}"
        )
