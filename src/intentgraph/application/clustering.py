"""Clustering engine for grouping files into AI-friendly clusters."""

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from uuid import uuid4

from ..domain.clustering import (
    ClusterConfig, ClusterMode, IndexLevel, ClusterFile, ClusterMetadata,
    ClusterSummary, CrossClusterDependency, ClusterIndex, ClusterResult
)
from ..domain.models import AnalysisResult, FileInfo


class ClusteringEngine:
    """Core clustering engine with pluggable algorithms."""
    
    def __init__(self, config: ClusterConfig):
        self.config = config
        
    def cluster_repository(self, analysis: AnalysisResult) -> ClusterResult:
        """Main entry point for clustering analysis results."""
        
        # Select clustering algorithm based on mode
        if self.config.mode == ClusterMode.ANALYSIS:
            clusters = self._dependency_based_clustering(analysis)
        elif self.config.mode == ClusterMode.REFACTORING:
            clusters = self._feature_based_clustering(analysis)
        elif self.config.mode == ClusterMode.NAVIGATION:
            clusters = self._size_optimized_clustering(analysis)
        else:
            raise ValueError(f"Unknown cluster mode: {self.config.mode}")
        
        # Apply size constraints and overlap rules
        clusters = self._apply_size_constraints(clusters, analysis)
        
        # Generate index and cluster files
        index = self._generate_index(clusters, analysis)
        cluster_files = self._generate_cluster_files(clusters, analysis)
        
        return ClusterResult(index=index, cluster_files=cluster_files)
    
    def _dependency_based_clustering(self, analysis: AnalysisResult) -> Dict[str, List[FileInfo]]:
        """Cluster files based on dependency relationships."""
        clusters = {}
        file_to_cluster = {}
        unassigned_files = list(analysis.files)
        
        # Start with architectural layers (domain, application, adapters)
        layer_patterns = {
            "domain": ["domain/", "/models.py", "/exceptions.py"],
            "application": ["application/", "/services.py", "/analyzer.py"], 
            "adapters": ["adapters/", "/parsers/", "/cli.py"],
            "infrastructure": ["infrastructure/", "/config/"],
        }
        
        for layer_name, patterns in layer_patterns.items():
            layer_files = []
            for file_info in unassigned_files[:]:  # Copy list to modify during iteration
                if any(pattern in str(file_info.path) for pattern in patterns):
                    layer_files.append(file_info)
                    unassigned_files.remove(file_info)
                    file_to_cluster[str(file_info.path)] = layer_name
            
            if layer_files:
                clusters[layer_name] = layer_files
        
        # Group remaining files by dependency relationships
        dependency_groups = self._find_dependency_groups(unassigned_files)
        for i, group in enumerate(dependency_groups):
            cluster_id = f"group_{i+1}"
            clusters[cluster_id] = group
            for file_info in group:
                file_to_cluster[str(file_info.path)] = cluster_id
        
        # Handle any remaining isolated files
        if unassigned_files:
            clusters["utilities"] = unassigned_files
            for file_info in unassigned_files:
                file_to_cluster[str(file_info.path)] = "utilities"
        
        return clusters
    
    def _feature_based_clustering(self, analysis: AnalysisResult) -> Dict[str, List[FileInfo]]:
        """Cluster files based on functional features."""
        clusters = {}
        
        # Define feature patterns
        feature_patterns = {
            "parsing": ["parser", "ast", "tree", "lexer"],
            "analysis": ["analyzer", "metrics", "complexity"],
            "cli": ["cli", "command", "main", "app"],
            "models": ["models", "schema", "types", "domain"],
            "io": ["file", "output", "input", "adapter"],
            "testing": ["test", "spec", "mock"],
            "config": ["config", "settings", "env"],
            "utils": ["util", "helper", "common", "shared"]
        }
        
        for file_info in analysis.files:
            file_path = str(file_info.path).lower()
            assigned = False
            
            # Try to match to a feature
            for feature_name, patterns in feature_patterns.items():
                if any(pattern in file_path for pattern in patterns):
                    if feature_name not in clusters:
                        clusters[feature_name] = []
                    clusters[feature_name].append(file_info)
                    assigned = True
                    break
            
            # Fallback to general category
            if not assigned:
                if "general" not in clusters:
                    clusters["general"] = []
                clusters["general"].append(file_info)
        
        return clusters
    
    def _size_optimized_clustering(self, analysis: AnalysisResult) -> Dict[str, List[FileInfo]]:
        """Cluster files to optimize for size constraints."""
        clusters = {}
        current_cluster = []
        current_size = 0.0
        cluster_count = 1
        
        # Sort files by size (largest first) for better packing
        sorted_files = sorted(analysis.files, key=lambda f: f.loc, reverse=True)
        
        for file_info in sorted_files:
            # Estimate file size in KB (rough: LOC * 50 bytes per line)
            file_size_kb = (file_info.loc * 50) / 1024
            
            # Check if adding this file would exceed size limit
            if current_size + file_size_kb > self.config.target_size_kb and current_cluster:
                # Finish current cluster
                clusters[f"cluster_{cluster_count}"] = current_cluster
                current_cluster = []
                current_size = 0.0
                cluster_count += 1
            
            # Add file to current cluster
            current_cluster.append(file_info)
            current_size += file_size_kb
        
        # Don't forget the last cluster
        if current_cluster:
            clusters[f"cluster_{cluster_count}"] = current_cluster
        
        return clusters
    
    def _find_dependency_groups(self, files: List[FileInfo]) -> List[List[FileInfo]]:
        """Find groups of files that depend on each other."""
        # Build file ID to FileInfo mapping
        id_to_file = {file_info.id: file_info for file_info in files}
        
        # Build dependency graph
        graph = defaultdict(set)
        for file_info in files:
            for dep_id in file_info.dependencies:
                if dep_id in id_to_file:
                    graph[file_info.id].add(dep_id)
                    graph[dep_id].add(file_info.id)  # Bidirectional for grouping
        
        # Find connected components
        visited = set()
        groups = []
        
        for file_info in files:
            if file_info.id not in visited:
                group = []
                self._dfs_collect(file_info.id, graph, visited, group, id_to_file)
                if group:
                    groups.append(group)
        
        return groups
    
    def _dfs_collect(self, file_id, graph, visited, group, id_to_file):
        """DFS to collect connected files."""
        if file_id in visited or file_id not in id_to_file:
            return
        
        visited.add(file_id)
        group.append(id_to_file[file_id])
        
        for neighbor_id in graph[file_id]:
            self._dfs_collect(neighbor_id, graph, visited, group, id_to_file)
    
    def _apply_size_constraints(self, clusters: Dict[str, List[FileInfo]], analysis: AnalysisResult) -> Dict[str, List[FileInfo]]:
        """Apply size constraints and handle overlarge/tiny clusters."""
        constrained_clusters = {}
        
        for cluster_id, files in clusters.items():
            # Calculate cluster size
            total_size_kb = sum((file_info.loc * 50) / 1024 for file_info in files)
            
            if total_size_kb > self.config.max_cluster_size_kb:
                # Split oversized cluster
                split_clusters = self._split_cluster(cluster_id, files)
                constrained_clusters.update(split_clusters)
            elif total_size_kb < self.config.min_cluster_size_kb:
                # Mark for potential merging (handled later)
                constrained_clusters[cluster_id] = files
            else:
                # Keep as-is
                constrained_clusters[cluster_id] = files
        
        # Merge tiny clusters if beneficial
        constrained_clusters = self._merge_tiny_clusters(constrained_clusters)
        
        return constrained_clusters
    
    def _split_cluster(self, cluster_id: str, files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """Split an oversized cluster into smaller ones."""
        # Simple strategy: split by file count first, then by dependency groups
        target_files_per_cluster = len(files) // 2 + 1
        
        split_clusters = {}
        for i in range(0, len(files), target_files_per_cluster):
            sub_cluster_id = f"{cluster_id}_part_{i//target_files_per_cluster + 1}"
            split_clusters[sub_cluster_id] = files[i:i + target_files_per_cluster]
        
        return split_clusters
    
    def _merge_tiny_clusters(self, clusters: Dict[str, List[FileInfo]]) -> Dict[str, List[FileInfo]]:
        """Merge clusters that are too small."""
        merged_clusters = {}
        tiny_clusters = []
        
        for cluster_id, files in clusters.items():
            total_size_kb = sum((file_info.loc * 50) / 1024 for file_info in files)
            
            if total_size_kb < self.config.min_cluster_size_kb:
                tiny_clusters.extend(files)
            else:
                merged_clusters[cluster_id] = files
        
        # Create merged cluster from tiny ones
        if tiny_clusters:
            merged_clusters["merged_utilities"] = tiny_clusters
        
        return merged_clusters
    
    def _generate_index(self, clusters: Dict[str, List[FileInfo]], analysis: AnalysisResult) -> ClusterIndex:
        """Generate the master index for cluster navigation."""
        cluster_summaries = []
        file_to_cluster_map = {}
        cross_cluster_deps = []
        
        for cluster_id, files in clusters.items():
            # Create cluster summary
            cluster_files = []
            total_size_kb = 0.0
            total_complexity = 0
            
            for file_info in files:
                file_size_kb = (file_info.loc * 50) / 1024
                total_size_kb += file_size_kb
                total_complexity += file_info.complexity_score
                
                cluster_files.append(ClusterFile(
                    path=file_info.path,
                    language=file_info.language,
                    size_kb=round(file_size_kb, 2),
                    complexity_score=file_info.complexity_score,
                    role=self._infer_file_role(file_info)
                ))
                
                file_to_cluster_map[str(file_info.path)] = cluster_id
            
            # Generate metadata
            metadata = ClusterMetadata(
                primary_concerns=self._extract_concerns(files),
                design_patterns=self._extract_patterns(files),
                key_abstractions=self._extract_abstractions(files),
                complexity_score=total_complexity,
                maintainability_index=sum(f.maintainability_index for f in files) / len(files) if files else 0.0
            )
            
            summary = ClusterSummary(
                cluster_id=cluster_id,
                name=self._generate_cluster_name(cluster_id, files),
                description=self._generate_cluster_description(cluster_id, files),
                files=cluster_files,
                file_count=len(files),
                total_size_kb=round(total_size_kb, 2),
                metadata=metadata
            )
            
            cluster_summaries.append(summary)
        
        # Generate cross-cluster dependencies
        cross_cluster_deps = self._find_cross_cluster_dependencies(clusters)
        
        return ClusterIndex(
            root_path=analysis.root,
            config=self.config,
            total_files=len(analysis.files),
            total_clusters=len(clusters),
            clusters=cluster_summaries,
            file_to_cluster_map=file_to_cluster_map,
            cross_cluster_dependencies=cross_cluster_deps,
            cluster_recommendations=self._generate_cluster_recommendations(cluster_summaries)
        )
    
    def _generate_cluster_files(self, clusters: Dict[str, List[FileInfo]], analysis: AnalysisResult) -> Dict[str, dict]:
        """Generate individual cluster data files."""
        cluster_files = {}
        
        for cluster_id, files in clusters.items():
            # Filter analysis result to only include files in this cluster
            cluster_data = {
                "cluster_id": cluster_id,
                "analyzed_at": analysis.analyzed_at,
                "root": str(analysis.root),
                "language_summary": {},
                "files": []
            }
            
            # Apply the same level filtering as the main analysis
            for file_info in files:
                if self.config.index_level == IndexLevel.BASIC:
                    # Minimal cluster data
                    filtered_file = {
                        "path": str(file_info.path),
                        "language": file_info.language,
                        "dependencies": [str(dep) for dep in file_info.dependencies],
                        "imports": file_info.imports,
                        "loc": file_info.loc,
                        "complexity_score": file_info.complexity_score,
                    }
                else:  # RICH
                    # Include more detail for rich clusters
                    filtered_file = {
                        "path": str(file_info.path),
                        "language": file_info.language,
                        "dependencies": [str(dep) for dep in file_info.dependencies],
                        "imports": file_info.imports,
                        "loc": file_info.loc,
                        "complexity_score": file_info.complexity_score,
                        "maintainability_index": file_info.maintainability_index,
                        "symbols": [
                            {
                                "name": symbol.name,
                                "symbol_type": symbol.symbol_type,
                                "line_start": symbol.line_start,
                                "is_exported": getattr(symbol, 'is_exported', False),
                            }
                            for symbol in file_info.symbols
                            if symbol.symbol_type in ["class", "function"]
                        ],
                        "exports": [
                            {
                                "name": export.name,
                                "export_type": export.export_type,
                            }
                            for export in file_info.exports
                        ],
                        "file_purpose": file_info.file_purpose,
                        "design_patterns": file_info.design_patterns,
                    }
                
                cluster_data["files"].append(filtered_file)
            
            cluster_files[cluster_id] = cluster_data
        
        return cluster_files
    
    def _infer_file_role(self, file_info: FileInfo) -> str:
        """Infer the role of a file in the codebase."""
        path_str = str(file_info.path).lower()
        
        if "interface" in path_str or "abstract" in path_str:
            return "interface"
        elif "test" in path_str:
            return "test"
        elif "util" in path_str or "helper" in path_str:
            return "utility"
        elif len(file_info.exports) > 3:
            return "interface"
        else:
            return "implementation"
    
    def _extract_concerns(self, files: List[FileInfo]) -> List[str]:
        """Extract primary concerns from cluster files."""
        concerns = set()
        for file_info in files:
            if file_info.file_purpose:
                concerns.add(file_info.file_purpose)
        return list(concerns)
    
    def _extract_patterns(self, files: List[FileInfo]) -> List[str]:
        """Extract design patterns from cluster files."""
        patterns = set()
        for file_info in files:
            patterns.update(file_info.design_patterns)
        return list(patterns)
    
    def _extract_abstractions(self, files: List[FileInfo]) -> List[str]:
        """Extract key abstractions from cluster files."""
        abstractions = set()
        for file_info in files:
            abstractions.update(file_info.key_abstractions)
        return list(abstractions)
    
    def _generate_cluster_name(self, cluster_id: str, files: List[FileInfo]) -> str:
        """Generate a human-readable cluster name."""
        if cluster_id in ["domain", "application", "adapters", "infrastructure"]:
            return f"{cluster_id.title()} Layer"
        elif "parser" in cluster_id.lower():
            return "Language Parsers"
        elif "test" in cluster_id.lower():
            return "Test Suite"
        elif "cli" in cluster_id.lower():
            return "Command Line Interface"
        else:
            return cluster_id.replace("_", " ").title()
    
    def _generate_cluster_description(self, cluster_id: str, files: List[FileInfo]) -> str:
        """Generate a description for the cluster."""
        file_count = len(files)
        primary_concerns = self._extract_concerns(files)
        
        if cluster_id == "domain":
            return f"Core domain models and business logic ({file_count} files)"
        elif cluster_id == "application":
            return f"Application services and use cases ({file_count} files)"
        elif cluster_id == "adapters":
            return f"External adapters and interfaces ({file_count} files)"
        elif primary_concerns:
            return f"{', '.join(primary_concerns)} ({file_count} files)"
        else:
            return f"Code cluster with {file_count} files"
    
    def _find_cross_cluster_dependencies(self, clusters: Dict[str, List[FileInfo]]) -> List[CrossClusterDependency]:
        """Find dependencies between clusters."""
        cluster_deps = []
        
        # Build cluster membership map
        file_to_cluster = {}
        for cluster_id, files in clusters.items():
            for file_info in files:
                file_to_cluster[file_info.id] = cluster_id
        
        # Find cross-cluster dependencies
        for cluster_id, files in clusters.items():
            dep_counts = defaultdict(int)
            
            for file_info in files:
                for dep_id in file_info.dependencies:
                    if dep_id in file_to_cluster:
                        target_cluster = file_to_cluster[dep_id]
                        if target_cluster != cluster_id:
                            dep_counts[target_cluster] += 1
            
            # Create dependency objects
            for target_cluster, count in dep_counts.items():
                strength = "high" if count >= 3 else "medium" if count >= 2 else "low"
                
                cluster_deps.append(CrossClusterDependency(
                    from_cluster=cluster_id,
                    to_cluster=target_cluster,
                    strength=strength,
                    dependency_type="imports",
                    file_count=count
                ))
        
        return cluster_deps
    
    def _generate_cluster_recommendations(self, clusters: List[ClusterSummary]) -> Dict[str, List[str]]:
        """Generate AI agent recommendations for different use cases."""
        recommendations = {
            "understanding_codebase": [],
            "making_changes": [], 
            "finding_bugs": [],
            "adding_features": []
        }
        
        for cluster in clusters:
            cluster_id = cluster.cluster_id
            
            # Recommend high-level clusters for understanding
            if cluster.metadata.complexity_score > 20:
                recommendations["understanding_codebase"].append(cluster_id)
            
            # Recommend interface clusters for making changes
            interface_files = [f for f in cluster.files if f.role == "interface"]
            if len(interface_files) > 0:
                recommendations["making_changes"].append(cluster_id)
            
            # Recommend complex clusters for bug finding
            if cluster.metadata.complexity_score > 30:
                recommendations["finding_bugs"].append(cluster_id)
            
            # Recommend extensible clusters for adding features
            if len(cluster.metadata.design_patterns) > 0:
                recommendations["adding_features"].append(cluster_id)
        
        return recommendations