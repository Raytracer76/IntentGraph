# AI Agent Workflows

This guide demonstrates how AI agents can leverage IntentGraph for different coding tasks.

## Overview

IntentGraph transforms the traditional "file scanning" approach into intelligent, context-aware workflows. Instead of constantly re-analyzing codebases, AI agents get pre-digested intelligence that fits within token limits.

## Workflow Patterns

### 1. Single-Shot Analysis
**Best for**: Small to medium codebases (<200KB)

```python
# AI Agent reads entire codebase intelligence at once
analysis = intentgraph.analyze(repo_path, level="minimal")  # ~10KB

# Now AI knows:
# - All file dependencies and relationships
# - Function signatures and exports
# - Code complexity and quality metrics
# - Architectural patterns and purposes
```

**Example Use Cases:**
- Code review for small repositories
- Quick bug identification
- Documentation generation
- Architectural assessment

### 2. Tiered Progressive Analysis
**Best for**: Medium to large codebases (200KB-2MB)

```python
# Start with overview
overview = intentgraph.analyze(repo_path, level="minimal")  # ~10KB

# Dive deeper into interesting areas
if needs_detailed_analysis:
    detailed = intentgraph.analyze(repo_path, level="medium")  # ~70KB

# Full analysis only when necessary
if comprehensive_audit_needed:
    full = intentgraph.analyze(repo_path, level="full")  # ~340KB
```

**Example Use Cases:**
- Large codebase exploration
- Incremental understanding
- Performance-sensitive analysis
- Token budget management

### 3. Intelligent Clustering Navigation
**Best for**: Massive codebases (2MB+)

```python
# Generate cluster analysis
cluster_result = intentgraph.cluster(repo_path, mode="analysis")

# AI reads navigation index first
with open(".intentgraph/index.json") as f:
    index = json.load(f)

# Get task-specific recommendations
target_clusters = index["cluster_recommendations"]["making_changes"]

# Load only relevant clusters
for cluster_id in target_clusters:
    with open(f".intentgraph/{cluster_id}.json") as f:
        cluster_data = json.load(f)
    # Process specific cluster...
```

**Example Use Cases:**
- Enterprise codebases
- Multi-service architectures
- Legacy system analysis
- Focused refactoring

## Real-World AI Agent Examples

### Code Review Agent

```python
def ai_code_review_workflow(repo_path, pr_files):
    """AI agent workflow for automated code review."""
    
    # 1. Get codebase intelligence
    analysis = intentgraph.analyze(repo_path, level="medium")
    
    # 2. Focus on changed files and their dependencies
    changed_files = set(pr_files)
    affected_files = set()
    
    for file_info in analysis["files"]:
        if file_info["path"] in changed_files:
            # Add dependencies of changed files
            affected_files.update(file_info["dependencies"])
    
    # 3. Analyze complexity and quality changes
    high_complexity = [
        f for f in analysis["files"] 
        if f["path"] in affected_files and f["complexity_score"] > 10
    ]
    
    # 4. Generate review comments
    review_comments = []
    for file_info in high_complexity:
        review_comments.append({
            "file": file_info["path"],
            "concern": "High complexity detected",
            "suggestion": "Consider refactoring for maintainability"
        })
    
    return review_comments
```

### Refactoring Assistant

```python
def ai_refactoring_workflow(repo_path, target_function):
    """AI agent workflow for safe refactoring."""
    
    # 1. Use refactoring-optimized clustering
    intentgraph.cluster(repo_path, mode="refactoring", size="10KB")
    
    with open(".intentgraph/index.json") as f:
        index = json.load(f)
    
    # 2. Find which cluster contains the target function
    target_cluster = None
    for file_path, cluster_id in index["file_to_cluster_map"].items():
        # Load cluster and check for target function
        with open(f".intentgraph/{cluster_id}.json") as f:
            cluster = json.load(f)
            
        for file_info in cluster["files"]:
            if file_info["path"] == file_path:
                for symbol in file_info.get("symbols", []):
                    if symbol["name"] == target_function:
                        target_cluster = cluster_id
                        break
    
    # 3. Load target cluster and analyze dependencies
    if target_cluster:
        with open(f".intentgraph/{target_cluster}.json") as f:
            cluster_data = json.load(f)
        
        # 4. Identify all usages and dependencies
        function_usages = find_function_usages(cluster_data, target_function)
        
        # 5. Plan safe refactoring steps
        refactoring_plan = create_refactoring_plan(function_usages)
        
        return refactoring_plan
    
    return None
```

### Documentation Generator

```python
def ai_documentation_workflow(repo_path):
    """AI agent workflow for comprehensive documentation."""
    
    # 1. Use navigation clustering for systematic coverage
    intentgraph.cluster(repo_path, mode="navigation", size="20KB")
    
    with open(".intentgraph/index.json") as f:
        index = json.load(f)
    
    documentation = {}
    
    # 2. Process each cluster systematically
    for cluster in index["clusters"]:
        cluster_id = cluster["cluster_id"]
        
        with open(f".intentgraph/{cluster_id}.json") as f:
            cluster_data = json.load(f)
        
        # 3. Extract public APIs from each cluster
        cluster_apis = []
        for file_info in cluster_data["files"]:
            for export in file_info.get("exports", []):
                if not export["name"].startswith("_"):  # Public API
                    cluster_apis.append({
                        "name": export["name"],
                        "type": export["export_type"],
                        "file": file_info["path"]
                    })
        
        # 4. Generate cluster documentation
        documentation[cluster_id] = {
            "name": cluster["name"],
            "description": cluster["description"],
            "public_apis": cluster_apis,
            "complexity": cluster["metadata"]["complexity_score"]
        }
    
    return documentation
```

## Task-Specific Recommendations

### Understanding New Codebase
```python
# Recommended approach:
# 1. Start with minimal analysis to get overview
# 2. Use analysis clustering to understand architecture
# 3. Focus on domain and application clusters first

analysis = intentgraph.analyze(repo_path, level="minimal")
intentgraph.cluster(repo_path, mode="analysis")

# Load architectural clusters first
priority_clusters = ["domain", "application", "adapters"]
```

### Making Targeted Changes
```python
# Recommended approach:
# 1. Use refactoring clustering for clean separation
# 2. Identify the specific feature cluster
# 3. Load only relevant clusters to minimize context

intentgraph.cluster(repo_path, mode="refactoring", size="10KB")

# Get recommendations for change-making
with open(".intentgraph/index.json") as f:
    index = json.load(f)
    
target_clusters = index["cluster_recommendations"]["making_changes"]
```

### Finding Bugs
```python
# Recommended approach:
# 1. Use medium analysis for complexity insights
# 2. Focus on high-complexity areas
# 3. Check cross-cluster dependencies for integration issues

analysis = intentgraph.analyze(repo_path, level="medium")

# Find high-complexity files
bug_candidates = [
    f for f in analysis["files"] 
    if f["complexity_score"] > 15 or f["maintainability_index"] < 50
]
```

### Adding New Features
```python
# Recommended approach:
# 1. Use analysis clustering to understand extension points
# 2. Identify design patterns and abstractions
# 3. Find clusters with good extensibility patterns

intentgraph.cluster(repo_path, mode="analysis")

with open(".intentgraph/index.json") as f:
    index = json.load(f)
    
extensible_clusters = index["cluster_recommendations"]["adding_features"]
```

## Performance Optimization Tips

### Token Budget Management
```python
# Estimate token usage before loading
def estimate_tokens(file_size_kb):
    return file_size_kb * 1024 / 4  # Rough estimate: 4 chars per token

# Choose appropriate level based on budget
if token_budget < 5000:
    level = "minimal"  # ~2500 tokens
elif token_budget < 20000:
    level = "medium"   # ~17500 tokens
else:
    level = "full"     # ~85000 tokens
```

### Caching Strategies
```python
# Cache analysis results for repeated use
import pickle
from pathlib import Path

def get_cached_analysis(repo_path, cache_dir=".intentgraph"):
    cache_file = Path(cache_dir) / "analysis.pkl"
    
    if cache_file.exists():
        # Check if cache is newer than any source file
        cache_time = cache_file.stat().st_mtime
        
        # If cache is fresh, use it
        if is_cache_fresh(repo_path, cache_time):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
    
    # Generate fresh analysis
    analysis = intentgraph.analyze(repo_path)
    
    # Cache for future use
    cache_file.parent.mkdir(exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(analysis, f)
    
    return analysis
```

### Incremental Analysis
```python
# Only re-analyze changed parts
def incremental_analysis(repo_path, changed_files):
    # Load existing analysis
    with open(".intentgraph/index.json") as f:
        index = json.load(f)
    
    # Find affected clusters
    affected_clusters = set()
    for file_path in changed_files:
        if file_path in index["file_to_cluster_map"]:
            cluster_id = index["file_to_cluster_map"][file_path]
            affected_clusters.add(cluster_id)
    
    # Re-analyze only affected clusters
    for cluster_id in affected_clusters:
        # Re-run analysis for this cluster's files
        cluster_files = get_cluster_files(cluster_id)
        updated_analysis = intentgraph.analyze_files(cluster_files)
        
        # Update cluster file
        with open(f".intentgraph/{cluster_id}.json", 'w') as f:
            json.dump(updated_analysis, f)
```

## Error Handling and Edge Cases

### Handling Large Files
```python
# Some files might be too large even for clustering
def handle_large_files(analysis):
    large_files = [
        f for f in analysis["files"] 
        if f.get("size_kb", 0) > 100  # Files larger than 100KB
    ]
    
    for file_info in large_files:
        # Create summary instead of full analysis
        summary = {
            "path": file_info["path"],
            "size_kb": file_info["size_kb"],
            "language": file_info["language"],
            "note": "File too large for detailed analysis",
            "key_exports": file_info["exports"][:5]  # Just top 5 exports
        }
        # Process summary...
```

### Memory Management
```python
# For very large repositories, process clusters one at a time
def memory_efficient_processing(index_path):
    with open(index_path) as f:
        index = json.load(f)
    
    results = []
    
    for cluster in index["clusters"]:
        cluster_id = cluster["cluster_id"]
        
        # Load cluster
        with open(f".intentgraph/{cluster_id}.json") as f:
            cluster_data = json.load(f)
        
        # Process cluster
        result = process_cluster(cluster_data)
        results.append(result)
        
        # Clear cluster data from memory
        del cluster_data
    
    return results
```

This workflow guide provides AI agents with concrete patterns for leveraging IntentGraph's intelligence across different coding scenarios, from simple analysis to complex refactoring tasks.