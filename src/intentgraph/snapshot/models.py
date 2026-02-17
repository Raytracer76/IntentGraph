"""Schema models for RepoSnapshot v1.

All models use Pydantic for validation and JSON serialization.
Deterministic ordering is enforced at the builder level.
"""

from collections.abc import Callable
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class PackageManager(str, Enum):
    """Detected package manager."""

    PNPM = "pnpm"
    NPM = "npm"
    YARN = "yarn"
    PIP = "pip"
    POETRY = "poetry"
    PIPENV = "pipenv"
    CONDA = "conda"
    UNKNOWN = "unknown"


class WorkspaceType(str, Enum):
    """Detected workspace/monorepo type."""

    PNPM_WORKSPACE = "pnpm-workspace"
    NPM_WORKSPACE = "npm-workspace"
    YARN_WORKSPACE = "yarn-workspace"
    LERNA = "lerna"
    NX = "nx"
    TURBOREPO = "turborepo"
    NONE = "none"


class ToolingInfo(BaseModel):
    """Information about detected tooling configuration."""

    typescript: str | None = Field(
        default=None, description="Path to tsconfig.json if present"
    )
    vitest: str | None = Field(
        default=None, description="Path to vitest config if present"
    )
    jest: str | None = Field(default=None, description="Path to jest config if present")
    eslint: str | None = Field(
        default=None, description="Path to eslint config if present"
    )
    prettier: str | None = Field(
        default=None, description="Path to prettier config if present"
    )
    pytest: str | None = Field(
        default=None, description="Path to pytest config if present"
    )
    ruff: str | None = Field(default=None, description="Path to ruff config if present")
    mypy: str | None = Field(default=None, description="Path to mypy config if present")

    class Config:
        """Pydantic config."""

        json_encoders = {Path: str}


class LanguageInfo(BaseModel):
    """Language statistics from analysis."""

    language: str = Field(..., description="Language name (python, javascript, etc)")
    file_count: int = Field(..., ge=0, description="Number of files in this language")
    total_bytes: int = Field(..., ge=0, description="Total bytes of source code")

    class Config:
        """Pydantic config."""

        # Ensure consistent ordering when serializing
        json_encoders: dict[type, Callable[[Any], Any]] = {}


class FileEntry(BaseModel):
    """Individual file information in the snapshot."""

    path: str = Field(..., description="Relative path from repository root")
    language: str = Field(..., description="Detected programming language")
    lines_of_code: int = Field(..., ge=0, description="Lines of code count")
    complexity: int = Field(..., ge=0, description="Cyclomatic complexity score")
    dependencies: list[str] = Field(
        default_factory=list, description="File UUIDs this file depends on"
    )
    imports: list[str] = Field(
        default_factory=list, description="Import statements as strings"
    )

    class Config:
        """Pydantic config."""

        json_encoders: dict[type, Callable[[Any], Any]] = {}


class StructureSnapshot(BaseModel):
    """Code structure from IntentGraph analysis."""

    analyzed_at: datetime = Field(
        ..., description="Timestamp when analysis was performed"
    )
    root_path: str = Field(..., description="Repository root path")
    languages: list[LanguageInfo] = Field(
        default_factory=list, description="Language statistics (sorted by name)"
    )
    file_index: dict[str, str] = Field(
        default_factory=dict, description="UUID to file path mapping (sorted by UUID)"
    )
    files: list[FileEntry] = Field(
        default_factory=list, description="File information (sorted by path)"
    )

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z",
            Path: str,
        }


class RuntimeSnapshot(BaseModel):
    """Runtime and tooling facts discovered from repository."""

    package_manager: PackageManager = Field(..., description="Detected package manager")
    workspace_type: WorkspaceType = Field(..., description="Detected workspace type")
    scripts: dict[str, str] = Field(
        default_factory=dict,
        description="Available scripts (sorted by name). Key=script name, Value=command",
    )
    tooling: ToolingInfo = Field(
        default_factory=lambda: ToolingInfo(),
        description="Detected tooling configuration",
    )
    python_version: str | None = Field(
        None, description="Required Python version from pyproject.toml or setup.py"
    )
    node_version: str | None = Field(
        None, description="Required Node version from .nvmrc or package.json"
    )

    class Config:
        """Pydantic config."""

        json_encoders: dict[type, Callable[[Any], Any]] = {}


class RepoSnapshot(BaseModel):
    """RepoSnapshot v1 - Complete repository intelligence snapshot.

    This is the top-level schema that combines code structure analysis
    with runtime/tooling facts. Designed for orchestrator preflight checks.

    Stability guarantees:
    - All arrays are sorted deterministically
    - Schema version embedded for forward compatibility
    - No external execution or network calls during generation
    """

    schema_version: str = Field(
        default="1.0.0", description="RepoSnapshot schema version"
    )
    snapshot_id: str = Field(
        ..., description="Unique identifier for this snapshot (UUID)"
    )
    created_at: datetime = Field(..., description="Snapshot creation timestamp")
    structure: StructureSnapshot = Field(..., description="Code structure analysis")
    runtime: RuntimeSnapshot = Field(..., description="Runtime and tooling facts")

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z",
            UUID: str,
            Path: str,
        }
