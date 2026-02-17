"""Builder for RepoSnapshot v1.

Combines IntentGraph analysis with runtime detection to produce
a complete, deterministic repository snapshot.
"""

import hashlib
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from ..application.analyzer import RepositoryAnalyzer
from ..domain.models import AnalysisResult
from .models import (
    FileEntry,
    LanguageInfo,
    RepoSnapshot,
    RuntimeSnapshot,
    StructureSnapshot,
)
from .runtime import RuntimeDetector


def _generate_deterministic_uuid(file_path: str, repo_root: str) -> UUID:
    """Generate deterministic UUID from file path.

    Uses SHA256 hash of canonical file path to generate stable UUID.

    Args:
        file_path: Relative file path
        repo_root: Repository root path

    Returns:
        Deterministic UUID based on path
    """
    # Create canonical identifier
    canonical = f"{repo_root}::{file_path}"
    hash_bytes = hashlib.sha256(canonical.encode()).digest()
    # Use first 16 bytes for UUID
    return UUID(bytes=hash_bytes[:16])


class RepoSnapshotBuilder:
    """Builds RepoSnapshot v1 from IntentGraph analysis + runtime detection."""

    def __init__(self, repo_root: Path) -> None:
        """Initialize builder with repository root.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root.resolve()
        self.runtime_detector = RuntimeDetector(self.repo_root)

    def build(self, analysis_result: AnalysisResult | None = None) -> RepoSnapshot:
        """Build complete RepoSnapshot.

        Args:
            analysis_result: Optional pre-computed IntentGraph analysis.
                           If None, will run analysis now.

        Returns:
            Complete RepoSnapshot with structure + runtime
        """
        # Run analysis if not provided
        if analysis_result is None:
            analyzer = RepositoryAnalyzer()
            analysis_result = analyzer.analyze(self.repo_root)

        # Build structure snapshot from analysis
        structure = self._build_structure(analysis_result)

        # Build runtime snapshot from detection
        runtime = self._build_runtime()

        # Combine into final snapshot
        snapshot = RepoSnapshot(
            snapshot_id=str(uuid4()),
            created_at=datetime.utcnow(),
            structure=structure,
            runtime=runtime,
        )

        return snapshot

    def _build_structure(self, analysis: AnalysisResult) -> StructureSnapshot:
        """Build structure snapshot from IntentGraph analysis.

        Ensures deterministic ordering:
        - languages: sorted by language name
        - file_index: sorted by UUID (keys)
        - files: sorted by path
        - UUIDs: deterministic hash-based UUIDs from file paths

        Args:
            analysis: IntentGraph AnalysisResult

        Returns:
            StructureSnapshot with sorted data and deterministic UUIDs
        """
        # Convert language summary to sorted list
        languages = [
            LanguageInfo(
                language=lang.value,
                file_count=summary.file_count,
                total_bytes=summary.total_bytes,
            )
            for lang, summary in analysis.language_summary.items()
        ]
        languages.sort(key=lambda x: x.language)

        # Build mapping of original UUID -> deterministic UUID
        uuid_mapping: dict[UUID, UUID] = {}
        repo_root = str(analysis.root)

        # Generate deterministic UUIDs for all files
        for file_info in analysis.files:
            file_path = str(file_info.path)
            deterministic_uuid = _generate_deterministic_uuid(file_path, repo_root)
            uuid_mapping[file_info.id] = deterministic_uuid

        # Build file_index with deterministic UUIDs (sorted by UUID)
        file_index: dict[str, str] = {}
        for file_info in analysis.files:
            det_uuid = uuid_mapping[file_info.id]
            file_index[str(det_uuid)] = str(file_info.path)
        # Sort by UUID for determinism
        file_index = dict(sorted(file_index.items()))

        # Convert files with deterministic UUIDs and sorted dependencies
        files = [
            FileEntry(
                path=str(file_info.path),
                language=file_info.language.value,
                lines_of_code=file_info.loc,
                complexity=file_info.complexity_score,
                dependencies=sorted(
                    [str(uuid_mapping.get(dep, dep)) for dep in file_info.dependencies]
                ),
                imports=sorted(file_info.imports),
            )
            for file_info in analysis.files
        ]
        # Sort files by path for determinism
        files.sort(key=lambda x: x.path)

        return StructureSnapshot(
            analyzed_at=analysis.analyzed_at,
            root_path=str(analysis.root),
            languages=languages,
            file_index=file_index,
            files=files,
        )

    def _build_runtime(self) -> RuntimeSnapshot:
        """Build runtime snapshot from detection.

        All detection is discovery-only (no execution).

        Returns:
            RuntimeSnapshot with sorted scripts
        """
        return RuntimeSnapshot(
            package_manager=self.runtime_detector.detect_package_manager(),
            workspace_type=self.runtime_detector.detect_workspace_type(),
            scripts=self.runtime_detector.detect_scripts(),  # Already sorted
            tooling=self.runtime_detector.detect_tooling(),
            python_version=self.runtime_detector.detect_python_version(),
            node_version=self.runtime_detector.detect_node_version(),
        )

    def build_json(
        self,
        analysis_result: AnalysisResult | None = None,
        indent: int = 2,
    ) -> str:
        """Build RepoSnapshot and serialize to JSON.

        Args:
            analysis_result: Optional pre-computed analysis
            indent: JSON indentation (default: 2)

        Returns:
            JSON string with deterministic formatting
        """
        snapshot = self.build(analysis_result)
        return snapshot.model_dump_json(indent=indent, exclude_none=False)
