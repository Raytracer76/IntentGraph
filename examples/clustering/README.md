# Clustering Examples

This directory contains examples demonstrating IntentGraph's intelligent clustering capabilities for large codebase navigation and AI agent optimization.

## Overview

IntentGraph's clustering system breaks large codebases into manageable, AI-friendly chunks while preserving semantic relationships and providing intelligent navigation indexes.

## Examples

### 1. Large Codebase Navigation (`large_codebase_navigation.py`)

Demonstrates how to use clustering for navigating massive repositories that exceed AI token limits.

```bash
python large_codebase_navigation.py /path/to/large/repository
```

**Features:**
- Runs clustering analysis with optimal settings
- Shows AI navigation strategy based on cluster index
- Simulates AI agent workflows for different tasks
- Demonstrates intelligent cluster selection

**Output:**
```
🔍 Running clustering analysis on /path/to/repo
✅ Clustering complete! Output in ./cluster_analysis
📊 Repository Overview:
   Total files: 287
   Total clusters: 12
   Clustering mode: analysis

🧠 AI Navigation Strategy Demonstration
📁 Cluster Summaries:
   domain: Domain Layer
      Files: 8, Size: 14.2KB
      Complexity: 25
      Purpose: Core business logic and models
```

### 2. Cluster Mode Comparison (`cluster_mode_comparison.py`)

Compares all three clustering modes to help you choose the best strategy for your use case.

```bash
python cluster_mode_comparison.py /path/to/repository
```

**Features:**
- Tests analysis, refactoring, and navigation modes
- Provides statistical comparison of clustering results
- Shows mode-specific characteristics and use cases
- Demonstrates AI agent workflow recommendations

**Output:**
```
📊 Clustering Mode Comparison
Mode        Clusters   Avg Size   Avg Files  Avg Complexity
analysis    7          14.1       3.7        15.2
refactoring 8          12.3       3.3        12.8
navigation  8          13.7       3.3        14.1

🎯 Mode Characteristics:
ANALYSIS MODE:
  🏗️  Architecture: Dependency-based grouping for code understanding
     Best for: AI agents learning codebase structure
```

## Clustering Modes Explained

### Analysis Mode (`--cluster-mode analysis`)
- **Strategy**: Dependency-based clustering with smart overlap
- **Best for**: Code understanding, documentation, architecture analysis
- **Characteristics**: Groups files that heavily depend on each other
- **Overlap**: Allows central files in multiple clusters for context

### Refactoring Mode (`--cluster-mode refactoring`)  
- **Strategy**: Feature-based clustering with no overlap
- **Best for**: Making targeted changes, feature development, bug fixing
- **Characteristics**: Groups files by functional purpose and domain
- **Overlap**: None - clean separation for focused modifications

### Navigation Mode (`--cluster-mode navigation`)
- **Strategy**: Size-optimized clustering for token efficiency
- **Best for**: Large codebase exploration, systematic analysis
- **Characteristics**: Balanced clusters optimized for AI token limits
- **Overlap**: Minimal - prioritizes even distribution

## Cluster Size Options

```bash
# Small clusters for detailed analysis
--cluster-size 10KB

# Balanced clusters (default)
--cluster-size 15KB  

# Larger clusters for high-level overview
--cluster-size 20KB
```

## Index Detail Levels

```bash
# Simple file mapping
--index-level basic

# Full metadata with AI recommendations (default)
--index-level rich
```

## AI Agent Integration Patterns

### Pattern 1: Task-Based Navigation
```python
# Load cluster index
with open("cluster_analysis/index.json") as f:
    index = json.load(f)

# Get clusters for specific task
task_clusters = index["cluster_recommendations"]["making_changes"]

# Load only relevant clusters
for cluster_id in task_clusters:
    with open(f"cluster_analysis/{cluster_id}.json") as f:
        cluster_data = json.load(f)
    # Process cluster_data...
```

### Pattern 2: Progressive Exploration
```python
# Start with cluster overview
clusters = index["clusters"]
for cluster in clusters:
    print(f"{cluster['name']}: {cluster['description']}")
    
# Dive into interesting clusters
high_complexity = [c for c in clusters if c["metadata"]["complexity_score"] > 20]
for cluster in high_complexity:
    # Load full cluster data for detailed analysis
    ...
```

### Pattern 3: Dependency-Aware Analysis
```python
# Find clusters with high interdependence
cross_deps = index["cross_cluster_dependencies"]
highly_connected = {}

for dep in cross_deps:
    if dep["strength"] == "high":
        # Load both source and target clusters
        ...
```

## Real-World Use Cases

### AI Code Review Agent
```bash
# Use analysis mode for understanding code relationships
intentgraph . --cluster --cluster-mode analysis --cluster-size 15KB --output review_clusters

# Agent loads domain and application clusters first
# Then examines cross-cluster dependencies for architectural issues
```

### AI Refactoring Assistant  
```bash
# Use refactoring mode for focused changes
intentgraph . --cluster --cluster-mode refactoring --cluster-size 10KB --output refactor_clusters

# Agent loads specific feature clusters
# Makes changes without worrying about unrelated code
```

### AI Documentation Generator
```bash
# Use navigation mode for systematic coverage
intentgraph . --cluster --cluster-mode navigation --cluster-size 20KB --output doc_clusters

# Agent processes clusters sequentially
# Ensures complete documentation coverage
```

## Tips for AI Agents

1. **Always start with the index.json** - it contains cluster recommendations for your specific task
2. **Use cluster_recommendations** - pre-computed suggestions for common workflows
3. **Check cross_cluster_dependencies** - understand how clusters relate to each other  
4. **Monitor cluster size** - stay within your token limits
5. **Leverage metadata** - complexity scores and concerns guide prioritization

## Performance Notes

- Clustering adds ~10-20% to analysis time
- Memory usage scales linearly with repository size
- Cluster generation is deterministic (same input = same clusters)
- Index generation includes AI-friendly recommendations

## Next Steps

After running these examples, try:
1. Integrating clustering into your AI agent workflows
2. Experimenting with different cluster sizes for your use case
3. Building custom navigation logic using the cluster index
4. Creating specialized cluster processing for your domain

The clustering system transforms how AI agents work with large codebases - from overwhelming to intelligently navigable! 🚀