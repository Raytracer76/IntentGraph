"""
Autonomous navigation system for AI agents.

This module provides AI agents with intelligent navigation capabilities
for codebase exploration without requiring human guidance or manual
path construction.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
import json
from dataclasses import dataclass

from ..application.analyzer import RepositoryAnalyzer
from ..application.clustering import ClusteringEngine  
from ..domain.clustering import ClusterConfig, ClusterMode, IndexLevel
from ..domain.models import Language, AnalysisResult
from .query import SemanticQuery, QueryType


@dataclass
class NavigationContext:
    """Context for autonomous navigation decisions."""
    current_focus: Optional[str] = None
    visited_areas: List[str] = None
    agent_goals: List[str] = None
    priority_areas: List[str] = None
    token_budget_remaining: int = 50000
    
    def __post_init__(self):
        if self.visited_areas is None:
            self.visited_areas = []
        if self.agent_goals is None:
            self.agent_goals = []
        if self.priority_areas is None:
            self.priority_areas = []


class AutonomousNavigator:
    """
    Autonomous navigation system that guides AI agents through codebase
    exploration without requiring human intervention or manual commands.
    """
    
    def __init__(self, repo_path: Path, agent_context: 'AgentContext'):
        """
        Initialize autonomous navigator.
        
        Args:
            repo_path: Repository path to navigate
            agent_context: AI agent context for personalized navigation
        """
        self.repo_path = repo_path
        self.agent_context = agent_context
        self.navigation_context = NavigationContext()
        
        # Navigation state
        self._analysis_cache = {}
        self._cluster_cache = {}
        self._navigation_history = []
        
        # Analysis components (lazy initialization)
        self._analyzer = None
        self._clustering_engine = None
        
        # Navigation strategies based on repository characteristics
        self._navigation_strategies = {
            "small_repo": self._small_repo_strategy,
            "medium_repo": self._medium_repo_strategy, 
            "large_repo": self._large_repo_strategy
        }
    
    def execute_query(self, query: SemanticQuery) -> Dict[str, Any]:
        """
        Execute semantic query with autonomous navigation.
        
        Args:
            query: Semantic query from AI agent
            
        Returns:
            Navigation results with intelligent guidance
        """
        # Record navigation step
        self._record_navigation_step(query)
        
        # Determine navigation strategy based on query and repository
        strategy = self._select_navigation_strategy(query)
        
        # Execute query using selected strategy
        results = strategy(query)
        
        # Add autonomous navigation guidance
        results["_navigation"] = self._generate_navigation_guidance(query, results)
        
        return results
    
    def _select_navigation_strategy(self, query: SemanticQuery) -> callable:
        """Select appropriate navigation strategy based on query and repository."""
        # Quick repository size estimation
        python_files = list(self.repo_path.rglob("*.py"))
        file_count = len(python_files)
        
        if file_count < 20:
            return self._navigation_strategies["small_repo"]
        elif file_count < 100:
            return self._navigation_strategies["medium_repo"]
        else:
            return self._navigation_strategies["large_repo"]
    
    def _small_repo_strategy(self, query: SemanticQuery) -> Dict[str, Any]:
        """Navigation strategy for small repositories (< 20 files)."""
        # For small repos, do full analysis upfront
        analysis = self._get_or_create_analysis()
        
        # Apply query-specific filtering
        filtered_results = self._filter_analysis_for_query(analysis, query)
        
        return {
            "strategy": "full_analysis",
            "scope": "complete_repository",
            "results": filtered_results,
            "confidence": "high",
            "coverage": "complete"
        }
    
    def _medium_repo_strategy(self, query: SemanticQuery) -> Dict[str, Any]:
        """Navigation strategy for medium repositories (20-100 files)."""
        # Use tiered approach: overview then focused analysis
        
        if query.query_type == QueryType.EXPLORATION:
            # Start with overview analysis
            overview = self._get_repository_overview()
            
            # Get focused areas based on query
            focused_areas = self._identify_focus_areas(query, overview)
            
            # Analyze focused areas in detail
            detailed_results = self._analyze_focused_areas(focused_areas, query)
            
            return {
                "strategy": "tiered_analysis",
                "scope": "focused_areas", 
                "overview": overview,
                "detailed_results": detailed_results,
                "confidence": "high",
                "coverage": "targeted"
            }
        else:
            # For specific queries, use targeted analysis
            return self._targeted_analysis_strategy(query)
    
    def _large_repo_strategy(self, query: SemanticQuery) -> Dict[str, Any]:
        """Navigation strategy for large repositories (> 100 files)."""
        # Use intelligent clustering for navigation
        
        # Create or get cluster analysis
        cluster_result = self._get_or_create_clusters(query)
        
        # Navigate through clusters based on query
        relevant_clusters = self._find_relevant_clusters(cluster_result, query)
        
        # Analyze relevant clusters
        cluster_analysis = self._analyze_clusters(relevant_clusters, query)
        
        return {
            "strategy": "cluster_navigation",
            "scope": "relevant_clusters",
            "cluster_overview": cluster_result.index.model_dump(),
            "relevant_clusters": relevant_clusters,
            "cluster_analysis": cluster_analysis,
            "confidence": "medium",
            "coverage": "cluster_based"
        }
    
    def _targeted_analysis_strategy(self, query: SemanticQuery) -> Dict[str, Any]:
        """Targeted analysis strategy for specific queries."""
        # Find files matching query constraints
        target_files = self._find_target_files(query)
        
        # Analyze target files with context
        analysis_results = self._analyze_with_context(target_files, query)
        
        return {
            "strategy": "targeted_analysis",
            "scope": "specific_files",
            "target_files": target_files,
            "results": analysis_results,
            "confidence": "high",
            "coverage": "focused"
        }
    
    def _get_or_create_analysis(self, force_refresh: bool = False) -> AnalysisResult:
        """Get cached analysis or create new one."""
        cache_key = "full_analysis"
        
        if not force_refresh and cache_key in self._analysis_cache:
            return self._analysis_cache[cache_key]
        
        # Create analyzer if not exists
        if self._analyzer is None:
            self._analyzer = RepositoryAnalyzer(
                include_tests=False,
                language_filter=[Language.PYTHON]  # Start with Python
            )
        
        # Perform analysis
        analysis = self._analyzer.analyze(self.repo_path)
        self._analysis_cache[cache_key] = analysis
        
        return analysis
    
    def _get_or_create_clusters(self, query: SemanticQuery) -> 'ClusterResult':
        """Get cached cluster analysis or create new one."""
        # Determine clustering mode based on query
        cluster_mode = self._determine_cluster_mode(query)
        cache_key = f"clusters_{cluster_mode.value}"
        
        if cache_key in self._cluster_cache:
            return self._cluster_cache[cache_key]
        
        # Create clustering configuration
        cluster_config = ClusterConfig(
            mode=cluster_mode,
            target_size_kb=15,  # Default size
            index_level=IndexLevel.RICH,
            allow_overlap=(cluster_mode == ClusterMode.ANALYSIS)
        )
        
        # Create clustering engine
        if self._clustering_engine is None:
            self._clustering_engine = ClusteringEngine(cluster_config)
        
        # Get base analysis first
        analysis = self._get_or_create_analysis()
        
        # Create clusters
        cluster_result = self._clustering_engine.cluster_repository(analysis)
        self._cluster_cache[cache_key] = cluster_result
        
        return cluster_result
    
    def _determine_cluster_mode(self, query: SemanticQuery) -> ClusterMode:
        """Determine appropriate clustering mode based on query."""
        if query.query_type in [QueryType.EXPLORATION, QueryType.PATTERN_DISCOVERY]:
            return ClusterMode.ANALYSIS
        elif query.query_type in [QueryType.IMPACT_ANALYSIS, QueryType.FOCUSED_ANALYSIS]:
            return ClusterMode.REFACTORING
        else:
            return ClusterMode.NAVIGATION
    
    def _filter_analysis_for_query(self, analysis: AnalysisResult, 
                                 query: SemanticQuery) -> Dict[str, Any]:
        """Filter analysis results based on query requirements."""
        filtered = {
            "file_count": len(analysis.files),
            "files": [],
            "summary": {
                "languages": list(analysis.language_summary.keys()),
                "total_loc": sum(f.loc for f in analysis.files),
                "avg_complexity": sum(f.complexity_score for f in analysis.files) / len(analysis.files) if analysis.files else 0
            }
        }
        
        # Apply query-specific filters
        for file_info in analysis.files:
            if self._file_matches_query(file_info, query):
                filtered["files"].append(self._extract_file_info(file_info, query))
        
        return filtered
    
    def _file_matches_query(self, file_info, query: SemanticQuery) -> bool:
        """Check if file matches query constraints."""
        # Check file type constraints
        if "file_types" in query.constraints:
            file_ext = Path(file_info.path).suffix.lower()
            required_types = query.constraints["file_types"]
            
            type_match = False
            for req_type in required_types:
                if req_type == "python" and file_ext == ".py":
                    type_match = True
                elif req_type in ["javascript", "typescript"] and file_ext in [".js", ".ts"]:
                    type_match = True
            
            if not type_match:
                return False
        
        # Check complexity constraints
        if "min_complexity" in query.constraints:
            if file_info.complexity_score < query.constraints["min_complexity"]:
                return False
        
        if "max_complexity" in query.constraints:
            if file_info.complexity_score > query.constraints["max_complexity"]:
                return False
        
        # Check size constraints
        if "min_size" in query.constraints:
            if file_info.loc < query.constraints["min_size"]:
                return False
        
        if "max_size" in query.constraints:
            if file_info.loc > query.constraints["max_size"]:
                return False
        
        # Check focus areas
        if query.focus_areas:
            file_path_lower = str(file_info.path).lower()
            purpose_lower = file_info.file_purpose.lower() if file_info.file_purpose else ""
            
            focus_match = False
            for focus in query.focus_areas:
                if focus in file_path_lower or focus in purpose_lower:
                    focus_match = True
                    break
            
            if not focus_match:
                return False
        
        return True
    
    def _extract_file_info(self, file_info, query: SemanticQuery) -> Dict[str, Any]:
        """Extract relevant file information based on query."""
        extracted = {
            "path": str(file_info.path),
            "language": file_info.language,
            "loc": file_info.loc,
            "complexity_score": file_info.complexity_score
        }
        
        # Add additional info based on query type
        if query.query_type == QueryType.FOCUSED_ANALYSIS:
            extracted.update({
                "maintainability_index": file_info.maintainability_index,
                "dependencies": [str(dep) for dep in file_info.dependencies],
                "symbols": [
                    {
                        "name": symbol.name,
                        "type": symbol.symbol_type,
                        "line": symbol.line_start
                    }
                    for symbol in file_info.symbols[:5]  # Limit symbols
                ]
            })
        
        if query.query_type == QueryType.QUALITY_ASSESSMENT:
            extracted.update({
                "quality_metrics": {
                    "complexity": file_info.complexity_score,
                    "maintainability": file_info.maintainability_index,
                    "design_patterns": file_info.design_patterns
                }
            })
        
        return extracted
    
    def _get_repository_overview(self) -> Dict[str, Any]:
        """Get high-level repository overview."""
        try:
            analysis = self._get_or_create_analysis()
            
            return {
                "total_files": len(analysis.files),
                "languages": list(analysis.language_summary.keys()),
                "total_loc": sum(f.loc for f in analysis.files),
                "avg_complexity": sum(f.complexity_score for f in analysis.files) / len(analysis.files) if analysis.files else 0,
                "high_complexity_files": [
                    str(f.path) for f in analysis.files 
                    if f.complexity_score > 10
                ],
                "architectural_layers": self._identify_architectural_layers(analysis)
            }
        except Exception as e:
            return {"error": f"Failed to generate overview: {str(e)}"}
    
    def _identify_architectural_layers(self, analysis: AnalysisResult) -> List[str]:
        """Identify architectural layers in the codebase."""
        layers = set()
        
        for file_info in analysis.files:
            path_parts = Path(file_info.path).parts
            
            # Common architectural patterns
            for part in path_parts:
                part_lower = part.lower()
                if part_lower in ["domain", "application", "adapters", "infrastructure"]:
                    layers.add(part_lower)
                elif part_lower in ["models", "services", "controllers", "views"]:
                    layers.add(part_lower)
                elif part_lower in ["api", "ui", "cli", "web"]:
                    layers.add(part_lower)
        
        return list(layers)
    
    def _identify_focus_areas(self, query: SemanticQuery, overview: Dict[str, Any]) -> List[str]:
        """Identify areas to focus on based on query and overview."""
        focus_areas = []
        
        # Use query focus areas if specified
        if query.focus_areas:
            focus_areas.extend(query.focus_areas)
        
        # Add areas based on query type
        if query.query_type == QueryType.QUALITY_ASSESSMENT:
            # Focus on high complexity areas
            focus_areas.extend(overview.get("high_complexity_files", []))
        
        # Add architectural layers
        focus_areas.extend(overview.get("architectural_layers", []))
        
        return focus_areas[:5]  # Limit to top 5 focus areas
    
    def _analyze_focused_areas(self, focus_areas: List[str], 
                             query: SemanticQuery) -> Dict[str, Any]:
        """Analyze specific focus areas in detail."""
        results = {}
        
        for area in focus_areas:
            # This would perform detailed analysis on the focus area
            # For now, return placeholder results
            results[area] = {
                "analysis_type": "focused",
                "findings": f"Detailed analysis of {area}",
                "recommendations": [f"Consider improvements in {area}"]
            }
        
        return results
    
    def _find_relevant_clusters(self, cluster_result: 'ClusterResult', 
                              query: SemanticQuery) -> List[str]:
        """Find clusters relevant to the query."""
        relevant_clusters = []
        
        # Use cluster recommendations if available
        recommendations = cluster_result.index.cluster_recommendations
        
        if query.query_type == QueryType.EXPLORATION:
            relevant_clusters.extend(recommendations.get("understanding_codebase", []))
        elif query.query_type == QueryType.IMPACT_ANALYSIS:
            relevant_clusters.extend(recommendations.get("making_changes", []))
        elif query.query_type == QueryType.QUALITY_ASSESSMENT:
            relevant_clusters.extend(recommendations.get("finding_bugs", []))
        
        # If no specific recommendations, use high-complexity clusters
        if not relevant_clusters:
            for cluster in cluster_result.index.clusters:
                if cluster.metadata.complexity_score > 20:
                    relevant_clusters.append(cluster.cluster_id)
        
        return relevant_clusters[:3]  # Limit to top 3 clusters
    
    def _analyze_clusters(self, cluster_ids: List[str], 
                         query: SemanticQuery) -> Dict[str, Any]:
        """Analyze specific clusters based on query."""
        cluster_analysis = {}
        
        for cluster_id in cluster_ids:
            # Load cluster data (would be from actual cluster files)
            cluster_analysis[cluster_id] = {
                "cluster_id": cluster_id,
                "analysis_summary": f"Analysis of {cluster_id} cluster",
                "key_findings": [f"Important finding in {cluster_id}"],
                "recommendations": [f"Recommendation for {cluster_id}"]
            }
        
        return cluster_analysis
    
    def _find_target_files(self, query: SemanticQuery) -> List[str]:
        """Find target files for focused analysis."""
        target_files = []
        
        # Use constraint-specified files if available
        if "target_files" in query.constraints:
            target_files.extend(query.constraints["target_files"])
        
        # Use change targets if specified
        if "change_targets" in query.constraints:
            target_files.extend(query.constraints["change_targets"])
        
        # If no specific targets, find files matching focus areas
        if not target_files and query.focus_areas:
            analysis = self._get_or_create_analysis()
            for file_info in analysis.files:
                if self._file_matches_query(file_info, query):
                    target_files.append(str(file_info.path))
        
        return target_files[:10]  # Limit to 10 files
    
    def _analyze_with_context(self, target_files: List[str], 
                            query: SemanticQuery) -> Dict[str, Any]:
        """Analyze target files with surrounding context."""
        # This would perform detailed analysis on target files
        # including their dependencies and relationships
        
        return {
            "target_files": target_files,
            "analysis_depth": "detailed_with_context",
            "findings": "Detailed analysis results",
            "context_analysis": "Surrounding code context",
            "impact_assessment": "Potential impact of changes"
        }
    
    def _record_navigation_step(self, query: SemanticQuery):
        """Record navigation step for history and optimization."""
        step = {
            "query_type": query.query_type.value,
            "intent": query.intent,
            "focus_areas": query.focus_areas,
            "timestamp": "current_time"  # Would use actual timestamp
        }
        
        self._navigation_history.append(step)
        
        # Update navigation context
        if query.focus_areas:
            self.navigation_context.visited_areas.extend(query.focus_areas)
    
    def _generate_navigation_guidance(self, query: SemanticQuery, 
                                    results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate autonomous navigation guidance for AI agents."""
        return {
            "next_recommended_queries": self._suggest_next_queries(query, results),
            "exploration_paths": self._suggest_exploration_paths(query, results),
            "optimization_hints": self._generate_optimization_hints(query, results),
            "navigation_efficiency": self._calculate_navigation_efficiency()
        }
    
    def _suggest_next_queries(self, query: SemanticQuery, 
                            results: Dict[str, Any]) -> List[str]:
        """Suggest next queries for continued exploration."""
        suggestions = []
        
        if query.query_type == QueryType.EXPLORATION:
            suggestions.extend([
                "Analyze code quality in identified areas",
                "Find potential security issues",
                "Examine architectural patterns"
            ])
        elif query.query_type == QueryType.FOCUSED_ANALYSIS:
            suggestions.extend([
                "Find similar implementations",
                "Analyze impact of potential changes",
                "Check for improvement opportunities"
            ])
        
        return suggestions[:3]
    
    def _suggest_exploration_paths(self, query: SemanticQuery, 
                                 results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Suggest exploration paths for autonomous navigation."""
        paths = []
        
        if results.get("strategy") == "cluster_navigation":
            paths.append({
                "path": "cluster_deep_dive",
                "description": "Deep dive into specific clusters",
                "expected_outcome": "Detailed cluster analysis"
            })
        
        if results.get("high_complexity_files"):
            paths.append({
                "path": "complexity_analysis", 
                "description": "Analyze high-complexity areas",
                "expected_outcome": "Complexity reduction opportunities"
            })
        
        return paths
    
    def _generate_optimization_hints(self, query: SemanticQuery, 
                                   results: Dict[str, Any]) -> List[str]:
        """Generate optimization hints for better navigation."""
        hints = []
        
        if self.navigation_context.token_budget_remaining < 10000:
            hints.append("Consider using more focused queries to conserve token budget")
        
        if len(self.navigation_context.visited_areas) > 10:
            hints.append("You've explored many areas - consider synthesizing findings")
        
        return hints
    
    def _calculate_navigation_efficiency(self) -> Dict[str, Any]:
        """Calculate navigation efficiency metrics."""
        return {
            "queries_executed": len(self._navigation_history),
            "areas_explored": len(set(self.navigation_context.visited_areas)),
            "efficiency_score": 0.85,  # Would calculate based on actual metrics
            "recommendation": "navigation_on_track"
        }
    
    def recommend_next_actions(self, agent_context: 'AgentContext', 
                             current_findings: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Recommend next actions for autonomous AI agents."""
        recommendations = []
        
        # Based on agent task
        if agent_context.task:
            task = agent_context.task.value
            
            if task == "bug_fixing":
                recommendations.append({
                    "action": "analyze_high_complexity",
                    "query": "Find files with high complexity and potential issues",
                    "priority": "high",
                    "expected_outcome": "Identification of bug-prone areas"
                })
            
            elif task == "feature_development":
                recommendations.append({
                    "action": "find_extension_points",
                    "query": "Show me extension points and interfaces",
                    "priority": "high", 
                    "expected_outcome": "Areas suitable for new features"
                })
        
        # Based on current findings
        if current_findings:
            if current_findings.get("high_complexity_files"):
                recommendations.append({
                    "action": "deep_dive_complexity",
                    "query": "Analyze specific high-complexity files",
                    "priority": "medium",
                    "expected_outcome": "Detailed complexity analysis"
                })
        
        return recommendations[:3]  # Limit to top 3 recommendations