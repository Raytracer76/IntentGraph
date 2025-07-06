"""
CodebaseAgent - Primary AI-native interface for autonomous codebase interaction.

This class provides AI agents with intelligent, context-aware access to codebase
intelligence without requiring human intervention or manual command construction.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from ..application.analyzer import RepositoryAnalyzer
from ..application.clustering import ClusteringEngine
from ..domain.clustering import ClusterConfig, ClusterMode, IndexLevel
from .manifest import get_capabilities_manifest
from .query import QueryBuilder, SemanticQuery
from .response import ResponseOptimizer, TokenBudget
from .navigation import AutonomousNavigator


class AgentTask(str, Enum):
    """Common AI agent task types for optimized responses."""
    CODE_UNDERSTANDING = "code_understanding"
    BUG_FIXING = "bug_fixing" 
    FEATURE_DEVELOPMENT = "feature_development"
    CODE_REVIEW = "code_review"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    SECURITY_AUDIT = "security_audit"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    DEPENDENCY_ANALYSIS = "dependency_analysis"


@dataclass
class AgentContext:
    """Context information about the AI agent for optimized responses."""
    agent_type: str = "general"
    task: Optional[AgentTask] = None
    token_budget: int = 50000  # Default ~50K tokens
    preferred_detail_level: str = "adaptive"  # adaptive, minimal, medium, full
    response_format: str = "structured"  # structured, narrative, code_focused
    expertise_level: str = "intermediate"  # beginner, intermediate, expert
    specific_interests: List[str] = None  # e.g., ["security", "performance"]
    
    def __post_init__(self):
        if self.specific_interests is None:
            self.specific_interests = []


class CodebaseAgent:
    """
    AI-native interface for autonomous codebase interaction.
    
    Provides intelligent, context-aware access to structured codebase intelligence
    without requiring human mediation or manual command construction.
    """
    
    def __init__(self, repo_path: Union[str, Path], agent_context: Dict[str, Any] = None):
        """
        Initialize AI agent interface to codebase.
        
        Args:
            repo_path: Path to repository to analyze
            agent_context: Dictionary with agent context information
        """
        self.repo_path = Path(repo_path)
        self.context = AgentContext(**(agent_context or {}))
        self.token_budget = TokenBudget(self.context.token_budget)
        
        # Initialize core components
        self._analyzer = None
        self._clustering_engine = None
        self._navigator = None
        self._response_optimizer = None
        self._analysis_cache = {}
        
        # Perform initial repository scan for agent orientation
        self._initialize_agent_interface()
    
    def _initialize_agent_interface(self):
        """Initialize the agent interface with repository intelligence."""
        # Lazy initialization - only analyze when needed
        self._navigator = AutonomousNavigator(self.repo_path, self.context)
        self._response_optimizer = ResponseOptimizer(self.context, self.token_budget)
        
        # Quick repository scan for agent orientation
        self._repo_overview = self._get_repository_overview()
    
    def _get_repository_overview(self) -> Dict[str, Any]:
        """Get high-level repository overview for agent orientation."""
        try:
            # Quick file scan without full analysis
            python_files = list(self.repo_path.rglob("*.py"))
            js_files = list(self.repo_path.rglob("*.js")) + list(self.repo_path.rglob("*.ts"))
            
            return {
                "path": str(self.repo_path),
                "total_python_files": len(python_files),
                "total_js_files": len(js_files),
                "estimated_size": "small" if len(python_files) < 50 else "medium" if len(python_files) < 200 else "large",
                "has_tests": any(("test" in str(f) or "spec" in str(f)) for f in python_files + js_files),
                "framework_hints": self._detect_frameworks(python_files + js_files)
            }
        except Exception:
            return {"path": str(self.repo_path), "scan_error": True}
    
    def _detect_frameworks(self, files: List[Path]) -> List[str]:
        """Quick framework detection for agent context."""
        frameworks = []
        
        # Sample first few files for framework hints
        for file_path in files[:10]:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')[:1000]  # First 1KB
                if 'django' in content.lower():
                    frameworks.append('Django')
                elif 'flask' in content.lower():
                    frameworks.append('Flask')
                elif 'fastapi' in content.lower():
                    frameworks.append('FastAPI')
                elif 'react' in content.lower():
                    frameworks.append('React')
                elif 'vue' in content.lower():
                    frameworks.append('Vue')
            except Exception:
                continue
        
        return list(set(frameworks))
    
    @property
    def capabilities(self) -> Dict[str, Any]:
        """Get self-describing capabilities manifest for this agent interface."""
        return get_capabilities_manifest(self._repo_overview)
    
    def query(self, request: Union[str, SemanticQuery], **kwargs) -> Dict[str, Any]:
        """
        Execute semantic query against codebase intelligence.
        
        Args:
            request: Natural language query or SemanticQuery object
            **kwargs: Additional query parameters
            
        Returns:
            Optimized response based on agent context and token budget
            
        Examples:
            >>> agent.query("Find files with high complexity")
            >>> agent.query("Show me the API endpoints")
            >>> agent.query("What are the main architectural components?")
            >>> agent.query("Find security vulnerabilities")
        """
        # Convert string to semantic query
        if isinstance(request, str):
            query_builder = QueryBuilder(self.context, self._repo_overview)
            query = query_builder.from_natural_language(request, **kwargs)
        else:
            query = request
        
        # Execute query using navigation system
        raw_results = self._navigator.execute_query(query)
        
        # Optimize response for agent context and token budget
        optimized_response = self._response_optimizer.optimize_response(
            raw_results, query, self.token_budget
        )
        
        return optimized_response
    
    def explore(self, focus_area: Optional[str] = None) -> Dict[str, Any]:
        """
        Autonomous exploration of codebase structure.
        
        Args:
            focus_area: Optional area to focus exploration (e.g., "security", "performance")
            
        Returns:
            Structured exploration results with navigation recommendations
        """
        exploration_query = QueryBuilder(self.context, self._repo_overview).create_exploration_query(focus_area)
        return self.query(exploration_query)
    
    def recommend_next_actions(self, current_findings: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get AI-native recommendations for next analysis steps.
        
        Args:
            current_findings: Optional current analysis results to build upon
            
        Returns:
            List of recommended actions with queries and expected outcomes
        """
        return self._navigator.recommend_next_actions(self.context, current_findings)
    
    def get_focused_analysis(self, files: List[str], analysis_type: str = "adaptive") -> Dict[str, Any]:
        """
        Get focused analysis on specific files based on agent task.
        
        Args:
            files: List of file paths to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Focused analysis results optimized for agent context
        """
        query = QueryBuilder(self.context, self._repo_overview).create_focused_query(files, analysis_type)
        return self.query(query)
    
    def navigate_to_implementation(self, concept: str) -> Dict[str, Any]:
        """
        Navigate directly to implementation of a concept or feature.
        
        Args:
            concept: Concept to find implementation for (e.g., "user authentication", "payment processing")
            
        Returns:
            Navigation results with implementation locations and context
        """
        navigation_query = QueryBuilder(self.context, self._repo_overview).create_navigation_query(concept)
        return self.query(navigation_query)
    
    def analyze_impact(self, proposed_changes: List[str]) -> Dict[str, Any]:
        """
        Analyze impact of proposed changes on codebase.
        
        Args:
            proposed_changes: List of files or components that would be changed
            
        Returns:
            Impact analysis with affected files, dependencies, and risk assessment
        """
        impact_query = QueryBuilder(self.context, self._repo_overview).create_impact_query(proposed_changes)
        return self.query(impact_query)
    
    def get_token_budget_remaining(self) -> int:
        """Get remaining token budget for this session."""
        return self.token_budget.remaining()
    
    def optimize_for_task(self, task: AgentTask) -> 'CodebaseAgent':
        """
        Optimize agent interface for specific task type.
        
        Args:
            task: Task type to optimize for
            
        Returns:
            Self (for method chaining)
        """
        self.context.task = task
        self._response_optimizer = ResponseOptimizer(self.context, self.token_budget)
        return self
    
    def set_token_budget(self, budget: int) -> 'CodebaseAgent':
        """
        Set token budget for responses.
        
        Args:
            budget: New token budget
            
        Returns:
            Self (for method chaining)
        """
        self.token_budget = TokenBudget(budget)
        self._response_optimizer = ResponseOptimizer(self.context, self.token_budget)
        return self
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"CodebaseAgent(repo='{self.repo_path}', task='{self.context.task}', budget={self.token_budget.total})"