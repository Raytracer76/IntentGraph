"""Generate traditional IntentGraph analysis of the intentgraph repository.

This example shows the traditional IntentGraph output format focusing on
code structure, symbols, and dependencies.
"""

from pathlib import Path
from intentgraph import RepositoryAnalyzer
import json


def main():
    """Generate traditional IntentGraph analysis."""
    # Analyze current repository
    repo_path = Path(__file__).parent.parent.parent
    print(f"Analyzing repository: {repo_path}")

    analyzer = RepositoryAnalyzer()
    result = analyzer.analyze(repo_path)

    # Convert to JSON-serializable format
    output = {
        "repository": str(repo_path),
        "analyzed_files": len(result.files),
        "language_summary": {
            lang.value: {
                "file_count": summary.file_count,
                "total_bytes": summary.total_bytes
            }
            for lang, summary in result.language_summary.items()
        },
        "files": [
            {
                "id": str(f.id),
                "path": str(f.path),
                "language": f.language.value,
                "lines_of_code": f.loc,
                "complexity_score": f.complexity_score,
                "maintainability_index": round(f.maintainability_index, 2) if f.maintainability_index else None,
                "imports": sorted(f.imports) if f.imports else [],
                "dependencies": [str(dep) for dep in f.dependencies],
                "symbols_count": len(f.symbols) if f.symbols else 0
            }
            for f in sorted(result.files, key=lambda x: x.path)
        ]
    }

    # Save to file
    output_path = Path(__file__).parent / "intentgraph_traditional.json"
    json_output = json.dumps(output, indent=2)
    output_path.write_text(json_output)

    print(f"\n✅ Generated traditional analysis:")
    print(f"   Output: {output_path}")
    print(f"   Size: {len(json_output):,} bytes")
    print(f"   Files: {len(result.files)}")
    print(f"   Languages: {', '.join(output['language_summary'].keys())}")


if __name__ == "__main__":
    main()
