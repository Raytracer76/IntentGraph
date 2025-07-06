#!/usr/bin/env python3
"""
Example: Comparing Different Clustering Modes

This example demonstrates the three clustering modes available in IntentGraph:
- Analysis: Dependency-based clustering for code understanding
- Refactoring: Feature-based clustering for making targeted changes
- Navigation: Size-optimized clustering for large codebase exploration
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any


def run_clustering_mode(repo_path: str, mode: str, size: str = "15KB") -> Dict[str, Any]:
    """
    Run IntentGraph clustering with a specific mode.
    
    Args:
        repo_path: Path to the repository to analyze
        mode: Clustering mode (analysis, refactoring, navigation)
        size: Target cluster size
        
    Returns:
        Dictionary containing the cluster index
    """
    output_dir = f"./cluster_{mode}_mode"
    
    print(f"🔍 Running {mode} mode clustering...")
    
    # Clean up previous run
    if Path(output_dir).exists():
        import shutil
        shutil.rmtree(output_dir)
    
    # Run IntentGraph with specified clustering mode
    cmd = [
        "intentgraph",
        repo_path,
        "--cluster",
        "--cluster-mode", mode,
        "--cluster-size", size,
        "--index-level", "rich",
        "--output", output_dir,
        "--format", "pretty"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error running {mode} mode: {result.stderr}")
        return {}
    
    # Load and return the index
    index_path = Path(output_dir) / "index.json"
    if index_path.exists():
        with open(index_path, 'r') as f:
            index = json.load(f)
            index["_output_dir"] = output_dir  # Store output dir for reference
            return index
    
    return {}


def analyze_clustering_results(mode: str, index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the results of a clustering mode.
    
    Args:
        mode: The clustering mode used
        index: The cluster index dictionary
        
    Returns:
        Analysis results dictionary
    """
    if not index:
        return {"error": f"No results for {mode} mode"}
    
    clusters = index.get("clusters", [])
    
    # Calculate statistics
    cluster_sizes = [cluster["total_size_kb"] for cluster in clusters]
    file_counts = [cluster["file_count"] for cluster in clusters]
    complexity_scores = [cluster["metadata"]["complexity_score"] for cluster in clusters]
    
    analysis = {
        "mode": mode,
        "total_clusters": len(clusters),
        "total_files": index.get("total_files", 0),
        "avg_cluster_size_kb": sum(cluster_sizes) / len(cluster_sizes) if cluster_sizes else 0,
        "avg_files_per_cluster": sum(file_counts) / len(file_counts) if file_counts else 0,
        "avg_complexity": sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0,
        "cluster_names": [cluster["name"] for cluster in clusters],
        "size_distribution": {
            "min": min(cluster_sizes) if cluster_sizes else 0,
            "max": max(cluster_sizes) if cluster_sizes else 0,
            "std": (sum((x - (sum(cluster_sizes) / len(cluster_sizes)))**2 for x in cluster_sizes) / len(cluster_sizes))**0.5 if cluster_sizes else 0
        }
    }
    
    return analysis


def compare_modes(analyses: List[Dict[str, Any]]) -> None:
    """
    Compare the results of different clustering modes.
    
    Args:
        analyses: List of analysis results from different modes
    """
    print("\n📊 Clustering Mode Comparison")
    print("=" * 60)
    
    # Create comparison table
    print(f"{'Mode':<12} {'Clusters':<10} {'Avg Size':<10} {'Avg Files':<10} {'Avg Complexity':<15}")
    print("-" * 60)
    
    for analysis in analyses:
        if "error" not in analysis:
            print(f"{analysis['mode']:<12} "
                  f"{analysis['total_clusters']:<10} "
                  f"{analysis['avg_cluster_size_kb']:<10.1f} "
                  f"{analysis['avg_files_per_cluster']:<10.1f} "
                  f"{analysis['avg_complexity']:<15.1f}")
    
    print("\n🎯 Mode Characteristics:")
    
    for analysis in analyses:
        if "error" not in analysis:
            mode = analysis["mode"]
            print(f"\n{mode.upper()} MODE:")
            print(f"  🏗️  Architecture: ", end="")
            
            if mode == "analysis":
                print("Dependency-based grouping for code understanding")
                print("     Best for: AI agents learning codebase structure")
                print("     Strategy: Groups files that depend on each other")
            elif mode == "refactoring":
                print("Feature-based grouping for targeted changes")
                print("     Best for: Making focused modifications to specific features")
                print("     Strategy: Groups files by functional purpose")
            elif mode == "navigation":
                print("Size-optimized grouping for large codebase exploration")
                print("     Best for: Systematic exploration of massive repositories")
                print("     Strategy: Balanced clusters optimized for token limits")
            
            print(f"  📁 Clusters generated: {analysis['total_clusters']}")
            print(f"  📐 Size consistency: ±{analysis['size_distribution']['std']:.1f}KB std dev")
            print(f"  🏷️  Cluster names: {', '.join(analysis['cluster_names'][:3])}")
            if len(analysis['cluster_names']) > 3:
                print(f"       ... and {len(analysis['cluster_names']) - 3} more")


def show_detailed_cluster_breakdown(analyses: List[Dict[str, Any]]) -> None:
    """
    Show detailed breakdown of clusters for each mode.
    
    Args:
        analyses: List of analysis results from different modes
    """
    print("\n🔍 Detailed Cluster Breakdown")
    print("=" * 60)
    
    for analysis in analyses:
        if "error" not in analysis:
            mode = analysis["mode"]
            print(f"\n{mode.upper()} MODE CLUSTERS:")
            
            # Load the actual index to show cluster details
            clusters = []
            # We would need to reload the index here, but for demo purposes, show the names
            for i, name in enumerate(analysis["cluster_names"]):
                print(f"  {i+1:2d}. {name}")
            
            print(f"     Total: {analysis['total_clusters']} clusters")
            print(f"     Coverage: {analysis['total_files']} files")


def demonstrate_ai_agent_recommendations(repo_path: str) -> None:
    """
    Show how different modes provide different AI agent recommendations.
    
    Args:
        repo_path: Path to the repository being analyzed
    """
    print(f"\n🤖 AI Agent Workflow Recommendations")
    print("=" * 60)
    
    workflows = {
        "analysis": [
            "🎯 Understanding new codebase",
            "📚 Documentation generation", 
            "🔍 Code review and audit",
            "🧠 Learning architecture patterns"
        ],
        "refactoring": [
            "⚡ Making targeted code changes",
            "🔧 Feature enhancement",
            "🐛 Bug fixing in specific modules",
            "🚀 Adding new functionality"
        ],
        "navigation": [
            "🗺️  Exploring massive repositories",
            "📊 Systematic code analysis",
            "🔬 Finding specific implementations",
            "📈 Performance optimization hunting"
        ]
    }
    
    for mode, use_cases in workflows.items():
        print(f"\n{mode.upper()} MODE - Best for:")
        for use_case in use_cases:
            print(f"  {use_case}")


def main():
    """Main demonstration function."""
    if len(sys.argv) < 2:
        print("Usage: python cluster_mode_comparison.py <repository_path>")
        print("Example: python cluster_mode_comparison.py /path/to/my/project")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    
    print("🚀 IntentGraph Clustering Mode Comparison")
    print("=" * 60)
    print(f"Repository: {repo_path}")
    
    # Test all three clustering modes
    modes = ["analysis", "refactoring", "navigation"]
    analyses = []
    
    try:
        for mode in modes:
            print(f"\n{'='*20} {mode.upper()} MODE {'='*20}")
            index = run_clustering_mode(repo_path, mode)
            analysis = analyze_clustering_results(mode, index)
            analyses.append(analysis)
            
            if "error" not in analysis:
                print(f"✅ {mode} mode complete: {analysis['total_clusters']} clusters generated")
            else:
                print(f"❌ {mode} mode failed: {analysis['error']}")
        
        # Compare all modes
        compare_modes(analyses)
        
        # Show detailed breakdown
        show_detailed_cluster_breakdown(analyses)
        
        # Show AI agent recommendations
        demonstrate_ai_agent_recommendations(repo_path)
        
        print(f"\n✨ Comparison Complete!")
        print(f"   All cluster outputs available in ./cluster_*_mode/ directories")
        print(f"   Choose the mode that best fits your AI agent's workflow!")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Comparison interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during comparison: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()