#!/usr/bin/env python3
"""
Example: Large Codebase Navigation with Intelligent Clustering

This example demonstrates how to use IntentGraph's clustering capabilities
for navigating and analyzing large codebases that exceed AI token limits.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any


def run_clustering_analysis(repo_path: str, output_dir: str) -> Dict[str, Any]:
    """
    Run IntentGraph clustering analysis on a repository.
    
    Args:
        repo_path: Path to the repository to analyze
        output_dir: Directory to store cluster output
        
    Returns:
        Dictionary containing the cluster index
    """
    print(f"🔍 Running clustering analysis on {repo_path}")
    
    # Run IntentGraph with clustering enabled
    cmd = [
        "intentgraph",
        repo_path,
        "--cluster",
        "--cluster-mode", "analysis",
        "--cluster-size", "15KB",
        "--index-level", "rich",
        "--output", output_dir,
        "--format", "pretty"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error running IntentGraph: {result.stderr}")
        sys.exit(1)
    
    print(f"✅ Clustering complete! Output in {output_dir}")
    print(result.stdout)
    
    # Load and return the index
    index_path = Path(output_dir) / "index.json"
    with open(index_path, 'r') as f:
        return json.load(f)


def demonstrate_ai_navigation_strategy(index: Dict[str, Any]) -> None:
    """
    Demonstrate how an AI agent would navigate clusters based on different tasks.
    
    Args:
        index: The cluster index dictionary
    """
    print("\n🧠 AI Navigation Strategy Demonstration")
    print("=" * 50)
    
    # Show cluster overview
    clusters = index["clusters"]
    print(f"📊 Repository Overview:")
    print(f"   Total files: {index['total_files']}")
    print(f"   Total clusters: {index['total_clusters']}")
    print(f"   Clustering mode: {index['config']['mode']}")
    
    # Display cluster summaries
    print(f"\n📁 Cluster Summaries:")
    for cluster in clusters:
        print(f"   {cluster['cluster_id']}: {cluster['name']}")
        print(f"      Files: {cluster['file_count']}, Size: {cluster['total_size_kb']}KB")
        print(f"      Complexity: {cluster['metadata']['complexity_score']}")
        print(f"      Purpose: {cluster['description']}")
        print()
    
    # Show AI recommendations for different tasks
    recommendations = index.get("cluster_recommendations", {})
    if recommendations:
        print(f"🎯 AI Task Recommendations:")
        for task, cluster_ids in recommendations.items():
            print(f"   {task.replace('_', ' ').title()}: {', '.join(cluster_ids)}")
        print()
    
    # Show cross-cluster dependencies
    cross_deps = index.get("cross_cluster_dependencies", [])
    if cross_deps:
        print(f"🔗 Cross-Cluster Dependencies:")
        for dep in cross_deps[:5]:  # Show first 5
            print(f"   {dep['from_cluster']} → {dep['to_cluster']} ({dep['strength']})")
        if len(cross_deps) > 5:
            print(f"   ... and {len(cross_deps) - 5} more")
        print()


def simulate_ai_agent_workflow(index: Dict[str, Any], output_dir: str, task: str) -> None:
    """
    Simulate how an AI agent would work with clustered data for a specific task.
    
    Args:
        index: The cluster index dictionary
        output_dir: Directory containing cluster files
        task: The task the AI agent is trying to accomplish
    """
    print(f"\n🤖 Simulating AI Agent Workflow: {task}")
    print("=" * 50)
    
    # Get recommended clusters for the task
    recommendations = index.get("cluster_recommendations", {})
    task_key = task.lower().replace(" ", "_")
    
    if task_key in recommendations:
        relevant_clusters = recommendations[task_key]
        print(f"📋 AI Agent Strategy:")
        print(f"   Task: {task}")
        print(f"   Recommended clusters: {', '.join(relevant_clusters)}")
        
        # Load and analyze each recommended cluster
        for cluster_id in relevant_clusters:
            cluster_path = Path(output_dir) / f"{cluster_id}.json"
            
            if cluster_path.exists():
                with open(cluster_path, 'r') as f:
                    cluster_data = json.load(f)
                
                print(f"\n🔍 Analyzing cluster: {cluster_id}")
                print(f"   Files in cluster: {len(cluster_data['files'])}")
                
                # Show key files for this cluster
                for file_data in cluster_data['files'][:3]:  # Show first 3 files
                    print(f"   📄 {file_data['path']}")
                    print(f"      Language: {file_data['language']}")
                    print(f"      LOC: {file_data['loc']}")
                    print(f"      Complexity: {file_data['complexity_score']}")
                    if file_data.get('symbols'):
                        symbols = [s['name'] for s in file_data['symbols'][:3]]
                        print(f"      Key symbols: {', '.join(symbols)}")
                
                if len(cluster_data['files']) > 3:
                    print(f"   ... and {len(cluster_data['files']) - 3} more files")
            else:
                print(f"   ⚠️  Cluster file not found: {cluster_path}")
    else:
        print(f"   ⚠️  No specific recommendations for task: {task}")
        print(f"   Available task types: {', '.join(recommendations.keys())}")


def main():
    """Main demonstration function."""
    if len(sys.argv) < 2:
        print("Usage: python large_codebase_navigation.py <repository_path>")
        print("Example: python large_codebase_navigation.py /path/to/my/project")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    output_dir = "./cluster_analysis"
    
    # Ensure output directory exists
    Path(output_dir).mkdir(exist_ok=True)
    
    print("🚀 IntentGraph Clustering Navigation Demo")
    print("=" * 50)
    
    try:
        # Run clustering analysis
        index = run_clustering_analysis(repo_path, output_dir)
        
        # Demonstrate AI navigation strategy
        demonstrate_ai_navigation_strategy(index)
        
        # Simulate AI agent workflows for different tasks
        tasks = [
            "understanding_codebase",
            "making_changes", 
            "finding_bugs",
            "adding_features"
        ]
        
        for task in tasks:
            simulate_ai_agent_workflow(index, output_dir, task)
        
        print(f"\n✨ Demo Complete!")
        print(f"   Cluster files available in: {output_dir}")
        print(f"   Load index.json to start AI navigation")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()