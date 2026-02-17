"""Shared fixtures and helpers for snapshot tests."""

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from intentgraph.snapshot import RepoSnapshotBuilder


def _ensure_git_repo(repo_path: Path) -> None:
    """Ensure directory is initialized as a git repository.

    Args:
        repo_path: Path to potential repository
    """
    if not (repo_path / ".git").exists():
        # Initialize git repo
        subprocess.run(
            ["git", "init"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
        # Add all files
        subprocess.run(
            ["git", "add", "."],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
        # Create initial commit
        subprocess.run(
            ["git", "commit", "-m", "test fixture", "--no-gpg-sign"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )


@pytest.fixture(scope="session", autouse=True)
def setup_fixture_repos() -> None:
    """Automatically initialize all fixture directories as git repos.

    This runs once per test session before any tests execute.
    """
    fixtures_dir = Path(__file__).parent / "fixtures"

    # Initialize each fixture directory as a git repo
    for fixture_dir in fixtures_dir.iterdir():
        if fixture_dir.is_dir() and fixture_dir.name != "expected":
            _ensure_git_repo(fixture_dir)


@pytest.fixture
def fixtures_dir() -> Path:
    """Get the fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def structure_only_repo(fixtures_dir: Path) -> Path:
    """Get structure-only fixture repo path."""
    return fixtures_dir / "structure_only"


@pytest.fixture
def node_pnpm_repo(fixtures_dir: Path) -> Path:
    """Get Node.js pnpm workspace fixture repo path."""
    return fixtures_dir / "node_pnpm"


@pytest.fixture
def python_poetry_repo(fixtures_dir: Path) -> Path:
    """Get Python poetry fixture repo path."""
    return fixtures_dir / "python_poetry"


@pytest.fixture
def malformed_toml_repo(fixtures_dir: Path) -> Path:
    """Get malformed TOML fixture repo path."""
    return fixtures_dir / "malformed_toml"


@pytest.fixture
def mixed_tooling_repo(fixtures_dir: Path) -> Path:
    """Get mixed tooling fixture repo path."""
    return fixtures_dir / "mixed_tooling"


def strip_timestamps(snapshot_dict: dict[str, Any]) -> dict[str, Any]:
    """Remove timestamp fields for stable comparison.

    Args:
        snapshot_dict: Snapshot dictionary

    Returns:
        Snapshot dict with timestamps removed
    """
    snapshot = snapshot_dict.copy()
    # Remove top-level timestamps
    snapshot.pop("snapshot_id", None)
    snapshot.pop("created_at", None)
    # Remove structure timestamps
    if "structure" in snapshot and isinstance(snapshot["structure"], dict):
        snapshot["structure"].pop("analyzed_at", None)
    return snapshot


def generate_snapshot_json(repo_path: Path) -> str:
    """Generate snapshot JSON for a repo.

    Args:
        repo_path: Path to repository

    Returns:
        JSON string of snapshot
    """
    builder = RepoSnapshotBuilder(repo_path)
    return builder.build_json(indent=2)


def compare_snapshots(
    actual_json: str, expected_json: str, *, ignore_timestamps: bool = True
) -> tuple[bool, str]:
    """Compare two snapshot JSONs.

    Args:
        actual_json: Actual snapshot JSON
        expected_json: Expected snapshot JSON
        ignore_timestamps: If True, strip timestamps before comparison

    Returns:
        Tuple of (is_equal, diff_message)
    """
    try:
        actual = json.loads(actual_json)
        expected = json.loads(expected_json)

        if ignore_timestamps:
            actual = strip_timestamps(actual)
            expected = strip_timestamps(expected)

        if actual == expected:
            return True, ""

        # Generate diff message
        actual_str = json.dumps(actual, indent=2, sort_keys=True)
        expected_str = json.dumps(expected, indent=2, sort_keys=True)

        import difflib

        diff = difflib.unified_diff(
            expected_str.splitlines(keepends=True),
            actual_str.splitlines(keepends=True),
            fromfile="expected",
            tofile="actual",
            lineterm="",
        )
        diff_lines = list(diff)[:50]  # Limit diff output
        return False, "".join(diff_lines)

    except json.JSONDecodeError as e:
        return False, f"JSON decode error: {e}"
