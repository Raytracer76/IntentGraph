"""RepoSnapshot v1 - Versioned repository intelligence for orchestrator preflight.

This module provides a stable, deterministic snapshot format that combines:
- Code structure analysis (from IntentGraph)
- Runtime/tooling facts (package manager, workspace config, available scripts)

Key guarantees:
- **Stable ordering**: All arrays sorted deterministically
- **Schema versioning**: Semantic versioning for backward compatibility
- **No execution**: Discovery only, no command execution or network calls
"""

from .builder import RepoSnapshotBuilder
from .models import (
    FileEntry,
    LanguageInfo,
    PackageManager,
    RepoSnapshot,
    RuntimeSnapshot,
    StructureSnapshot,
    ToolingInfo,
    WorkspaceType,
)

__all__ = [
    "FileEntry",
    "LanguageInfo",
    "PackageManager",
    "RepoSnapshot",
    "RepoSnapshotBuilder",
    "RuntimeSnapshot",
    "StructureSnapshot",
    "ToolingInfo",
    "WorkspaceType",
]
