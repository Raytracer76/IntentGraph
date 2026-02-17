"""Tests for runtime environment detection."""

from pathlib import Path

import pytest

from intentgraph.snapshot import RepoSnapshotBuilder
from intentgraph.snapshot.models import PackageManager, WorkspaceType


class TestRuntimeDetection:
    """Tests for runtime environment and tooling detection."""

    def test_structure_only_no_runtime(self, structure_only_repo: Path) -> None:
        """Structure-only repo should have minimal runtime info."""
        builder = RepoSnapshotBuilder(structure_only_repo)
        snapshot = builder.build()

        # No package manager detected
        assert snapshot.runtime.package_manager == PackageManager.UNKNOWN

        # No workspace
        assert snapshot.runtime.workspace_type == WorkspaceType.NONE

        # No scripts
        assert len(snapshot.runtime.scripts) == 0

        # No version specs
        assert snapshot.runtime.python_version is None
        assert snapshot.runtime.node_version is None

    def test_node_pnpm_detection(self, node_pnpm_repo: Path) -> None:
        """Node.js pnpm workspace should be detected correctly."""
        builder = RepoSnapshotBuilder(node_pnpm_repo)
        snapshot = builder.build()

        # Should detect pnpm
        assert (
            snapshot.runtime.package_manager == PackageManager.PNPM
        ), f"Expected pnpm, got {snapshot.runtime.package_manager}"

        # Should detect pnpm workspace
        assert (
            snapshot.runtime.workspace_type == WorkspaceType.PNPM_WORKSPACE
        ), f"Expected pnpm-workspace, got {snapshot.runtime.workspace_type}"

        # Should extract scripts
        assert len(snapshot.runtime.scripts) > 0, "No scripts extracted"
        assert "build" in snapshot.runtime.scripts, "build script not found"
        assert "test" in snapshot.runtime.scripts, "test script not found"

        # Scripts should be sorted
        script_keys = list(snapshot.runtime.scripts.keys())
        assert script_keys == sorted(script_keys), "Scripts not sorted"

        # Should detect Node version
        assert snapshot.runtime.node_version is not None, "Node version not detected"
        assert "18" in snapshot.runtime.node_version, "Unexpected Node version"

    def test_node_tooling_detection(self, node_pnpm_repo: Path) -> None:
        """Node.js tooling configs should be detected."""
        builder = RepoSnapshotBuilder(node_pnpm_repo)
        snapshot = builder.build()

        # Should detect TypeScript
        assert (
            snapshot.runtime.tooling.typescript is not None
        ), "TypeScript config not detected"
        assert (
            "tsconfig.json" in snapshot.runtime.tooling.typescript
        ), "tsconfig.json not in path"

        # Should detect Vitest
        assert (
            snapshot.runtime.tooling.vitest is not None
        ), "Vitest config not detected"

    def test_python_poetry_detection(self, python_poetry_repo: Path) -> None:
        """Python poetry project should be detected correctly."""
        builder = RepoSnapshotBuilder(python_poetry_repo)
        snapshot = builder.build()

        # Should detect poetry
        assert (
            snapshot.runtime.package_manager == PackageManager.POETRY
        ), f"Expected poetry, got {snapshot.runtime.package_manager}"

        # Should detect Python version
        assert (
            snapshot.runtime.python_version is not None
        ), "Python version not detected"
        assert "3.11" in snapshot.runtime.python_version, "Unexpected Python version"

    def test_python_tooling_detection(self, python_poetry_repo: Path) -> None:
        """Python tooling in pyproject.toml should be detected."""
        builder = RepoSnapshotBuilder(python_poetry_repo)
        snapshot = builder.build()

        # Should detect pytest config
        assert (
            snapshot.runtime.tooling.pytest is not None
        ), "pytest config not detected"
        assert (
            "pyproject.toml" in snapshot.runtime.tooling.pytest
        ), "pytest not in pyproject.toml"

        # Should detect ruff config
        assert snapshot.runtime.tooling.ruff is not None, "ruff config not detected"

        # Should detect mypy config
        assert snapshot.runtime.tooling.mypy is not None, "mypy config not detected"

    def test_mixed_tooling_precedence(self, mixed_tooling_repo: Path) -> None:
        """Mixed tooling configs should be detected with correct precedence."""
        builder = RepoSnapshotBuilder(mixed_tooling_repo)
        snapshot = builder.build()

        # Should detect Node version from .nvmrc
        assert (
            snapshot.runtime.node_version is not None
        ), "Node version not detected from .nvmrc"
        assert (
            "18.20.0" in snapshot.runtime.node_version
        ), "Unexpected Node version from .nvmrc"

        # Should detect ESLint
        assert (
            snapshot.runtime.tooling.eslint is not None
        ), "ESLint config not detected"
        assert (
            ".eslintrc.json" in snapshot.runtime.tooling.eslint
        ), "eslintrc.json not detected"

        # Should detect Prettier
        assert (
            snapshot.runtime.tooling.prettier is not None
        ), "Prettier config not detected"

        # Should detect Jest
        assert snapshot.runtime.tooling.jest is not None, "Jest config not detected"
        assert (
            "jest.config.js" in snapshot.runtime.tooling.jest
        ), "jest.config.js not detected"
