"""Generate RepoSnapshot v1 of the intentgraph repository.

This example shows the new RepoSnapshot v1 format which combines code structure
analysis with runtime environment detection in a deterministic, version-controlled
format.
"""

from pathlib import Path
from intentgraph.snapshot import RepoSnapshotBuilder
import json


def main():
    """Generate RepoSnapshot v1 analysis."""
    # Analyze current repository
    repo_path = Path(__file__).parent.parent.parent
    print(f"Analyzing repository: {repo_path}")

    builder = RepoSnapshotBuilder(repo_path)
    snapshot = builder.build()

    # Save to file
    output_path = Path(__file__).parent / "intentgraph_snapshot_v1.json"
    json_output = builder.build_json(indent=2)
    output_path.write_text(json_output)

    print(f"\n✅ Generated RepoSnapshot v1:")
    print(f"   Output: {output_path}")
    print(f"   Size: {len(json_output):,} bytes")
    print(f"   Schema: {snapshot.schema_version}")
    print(f"   Files: {len(snapshot.structure.files)}")
    print(f"   Languages: {', '.join(lang.language for lang in snapshot.structure.languages)}")
    print(f"\n   Runtime Environment:")
    print(f"   - Package Manager: {snapshot.runtime.package_manager}")
    print(f"   - Workspace Type: {snapshot.runtime.workspace_type}")
    print(f"   - Python Version: {snapshot.runtime.python_version}")
    print(f"   - Tooling Detected: {len([k for k, v in snapshot.runtime.tooling.dict().items() if v])}")
    print(f"   - Scripts: {len(snapshot.runtime.scripts or {})}")


if __name__ == "__main__":
    main()
