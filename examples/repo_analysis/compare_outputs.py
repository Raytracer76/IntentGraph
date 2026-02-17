"""Compare traditional IntentGraph output vs RepoSnapshot v1.

This script demonstrates the differences between the traditional IntentGraph
analysis format and the new RepoSnapshot v1 format.
"""

from pathlib import Path
import json


def load_outputs():
    """Load both output files."""
    base_path = Path(__file__).parent

    traditional_path = base_path / "intentgraph_traditional.json"
    snapshot_path = base_path / "intentgraph_snapshot_v1.json"

    if not traditional_path.exists() or not snapshot_path.exists():
        print("❌ Output files not found. Run generation scripts first:")
        print("   python generate_traditional_analysis.py")
        print("   python generate_snapshot_v1.py")
        return None, None

    with open(traditional_path) as f:
        traditional = json.load(f)

    with open(snapshot_path) as f:
        snapshot = json.load(f)

    return traditional, snapshot


def compare_structure(traditional, snapshot):
    """Compare structure analysis aspects."""
    print("\n📊 Structure Analysis Comparison")
    print("=" * 60)

    trad_files = traditional["analyzed_files"]
    snap_files = len(snapshot["structure"]["files"])

    print(f"\nFiles Analyzed:")
    print(f"  Traditional: {trad_files}")
    print(f"  Snapshot v1: {snap_files}")
    print(f"  Difference: {snap_files - trad_files} (snapshot includes test files by default)")

    print(f"\nLanguages Detected:")
    print(f"  Traditional: {', '.join(traditional['language_summary'].keys())}")
    print(f"  Snapshot v1: {', '.join(lang['language'] for lang in snapshot['structure']['languages'])}")

    print(f"\nFile Metadata:")
    print(f"  Traditional includes:")
    print(f"    - UUID (random)")
    print(f"    - Path, language, LOC")
    print(f"    - Complexity, maintainability")
    print(f"    - Imports, dependencies, symbols")
    print(f"  Snapshot v1 includes:")
    print(f"    - UUID (deterministic, SHA256-based)")
    print(f"    - Path, language, LOC")
    print(f"    - Complexity (Python only)")
    print(f"    - Imports, dependencies (UUIDs)")
    print(f"    - File index (UUID → path mapping)")


def compare_determinism(traditional, snapshot):
    """Compare determinism features."""
    print("\n🔒 Determinism Comparison")
    print("=" * 60)

    print("\nTraditional IntentGraph:")
    print("  ❌ UUIDs: Random (uuid4) - different on each run")
    print("  ❌ Timestamps: Not included")
    print("  ⚠️  Ordering: May vary")

    print("\nRepoSnapshot v1:")
    print("  ✅ UUIDs: Deterministic (SHA256 hash of canonical path)")
    print("  ✅ Timestamps: Included but excluded from comparisons")
    print("  ✅ Ordering: All arrays sorted (languages, files, imports, etc.)")
    print("  ✅ Cross-platform: Windows/Linux produce identical UUIDs")


def compare_runtime_detection(snapshot):
    """Show runtime detection (unique to RepoSnapshot)."""
    print("\n⚙️  Runtime Environment Detection (Snapshot v1 Only)")
    print("=" * 60)

    runtime = snapshot["runtime"]

    print(f"\nPackage Manager: {runtime['package_manager']}")
    print(f"Workspace Type: {runtime['workspace_type']}")
    print(f"Python Version: {runtime['python_version']}")
    print(f"Node Version: {runtime['node_version']}")

    print(f"\nTooling Detected:")
    tooling = runtime["tooling"]
    for tool, config in tooling.items():
        if config:
            print(f"  - {tool:20s}: {config}")

    scripts = runtime.get("scripts", {})
    if scripts:
        print(f"\nScripts ({len(scripts)}):")
        for name, command in sorted(scripts.items())[:5]:
            print(f"  - {name:20s}: {command[:50]}...")


def compare_use_cases():
    """Compare use cases for each format."""
    print("\n🎯 Use Case Comparison")
    print("=" * 60)

    print("\nTraditional IntentGraph:")
    print("  ✅ Deep code structure analysis")
    print("  ✅ Symbol-level information")
    print("  ✅ Detailed Python analysis (complexity, maintainability)")
    print("  ✅ Real-time exploration")
    print("  ❌ Not suitable for version control (random UUIDs)")
    print("  ❌ No runtime environment info")

    print("\nRepoSnapshot v1:")
    print("  ✅ Deterministic, version-controlled snapshots")
    print("  ✅ Change tracking over time")
    print("  ✅ Runtime environment detection")
    print("  ✅ Cross-platform consistency")
    print("  ✅ Stable for AI agent context")
    print("  ⚠️  Less detailed symbol information")
    print("  ⚠️  Currently Python-focused for complexity")


def main():
    """Run comparison."""
    print("🔍 IntentGraph Output Comparison")
    print("=" * 60)

    traditional, snapshot = load_outputs()

    if not traditional or not snapshot:
        return

    # File sizes
    trad_size = len(json.dumps(traditional))
    snap_size = len(json.dumps(snapshot))

    print(f"\n📦 File Sizes:")
    print(f"  Traditional: {trad_size:,} bytes")
    print(f"  Snapshot v1: {snap_size:,} bytes")
    print(f"  Difference: {snap_size - trad_size:+,} bytes")

    compare_structure(traditional, snapshot)
    compare_determinism(traditional, snapshot)
    compare_runtime_detection(snapshot)
    compare_use_cases()

    print("\n" + "=" * 60)
    print("✅ Comparison complete!")
    print("\nSee README.md for more details on when to use each format.")


if __name__ == "__main__":
    main()
