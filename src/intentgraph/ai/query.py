"""
Semantic query interface for AI-native codebase interaction.

This module enables AI agents to construct and execute semantic queries
against codebase intelligence without requiring human-crafted commands
or manual output handling.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import re
from pathlib import Path


class QueryType(str, Enum):
    """Types of semantic queries agents can make."""
    EXPLORATION = "exploration"           # High-level codebase understanding
    FOCUSED_ANALYSIS = "focused_analysis" # Deep dive on specific files/components
    NAVIGATION = "navigation"             # Find implementations of concepts
    IMPACT_ANALYSIS = "impact_analysis"   # Analyze change impact
    QUALITY_ASSESSMENT = "quality_assessment" # Code quality and metrics
    SECURITY_ANALYSIS = "security_analysis"   # Security patterns and vulnerabilities
    PATTERN_DISCOVERY = "pattern_discovery"   # Find design patterns and architectures
    DEPENDENCY_ANALYSIS = "dependency_analysis" # Dependency relationships and risks


class ResponsePriority(str, Enum):
    """Priority levels for response content."""
    ESSENTIAL = "essential"     # Must include in response
    IMPORTANT = "important"     # Include if token budget allows
    SUPPLEMENTARY = "supplementary" # Include only if ample budget
    CONTEXT = "context"         # Background information


@dataclass
class SemanticQuery:
    """
    Semantic query object for AI-native codebase interaction.
    
    Unlike traditional command-line queries, semantic queries express
    intent and context, allowing the system to intelligently determine
    the best approach and response format.
    """
    
    query_type: QueryType
    intent: str                          # Natural language intent
    focus_areas: List[str] = field(default_factory=list)  # Specific areas of interest
    constraints: Dict[str, Any] = field(default_factory=dict)  # Query constraints
    context: Dict[str, Any] = field(default_factory=dict)      # Agent context
    priority: ResponsePriority = ResponsePriority.IMPORTANT
    
    # Response optimization
    max_tokens: Optional[int] = None     # Maximum tokens in response
    preferred_format: str = "structured" # structured, narrative, code_focused
    detail_level: str = "adaptive"       # adaptive, minimal, medium, full
    
    # Navigation hints
    related_concepts: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary for processing."""
        return {
            "query_type": self.query_type.value,
            "intent": self.intent,
            "focus_areas": self.focus_areas,
            "constraints": self.constraints,
            "context": self.context,
            "priority": self.priority.value,
            "max_tokens": self.max_tokens,
            "preferred_format": self.preferred_format,
            "detail_level": self.detail_level,
            "related_concepts": self.related_concepts,
            "exclude_patterns": self.exclude_patterns
        }


class QueryBuilder:
    """
    Intelligent query builder that converts natural language and context
    into semantic queries optimized for AI agent needs.
    """
    
    def __init__(self, agent_context: 'AgentContext', repo_overview: Dict[str, Any]):
        """
        Initialize query builder with agent context.
        
        Args:
            agent_context: Information about the requesting AI agent
            repo_overview: High-level repository information
        """
        self.agent_context = agent_context
        self.repo_overview = repo_overview
        
        # Intent patterns for natural language parsing
        self.intent_patterns = {
            QueryType.EXPLORATION: [
                r"explore|overview|understand|architecture|structure|organization",
                r"what (is|are)|how (is|does)|main components|key files"
            ],
            QueryType.FOCUSED_ANALYSIS: [
                r"analyze|examine|deep dive|detailed analysis|focus on",
                r"(show|tell) me about|explain|describe in detail"
            ],
            QueryType.NAVIGATION: [
                r"find|locate|where (is|are)|navigate to|implementation",
                r"(search|look) for|contains|implements"
            ],
            QueryType.IMPACT_ANALYSIS: [
                r"impact|affect|change|modify|consequences|dependencies",
                r"what (would|will) happen|ripple effect|side effects"
            ],
            QueryType.QUALITY_ASSESSMENT: [
                r"quality|complexity|maintainability|technical debt|problems",
                r"(code|software) quality|metrics|assessment|review"
            ],
            QueryType.SECURITY_ANALYSIS: [
                r"security|vulnerability|vulnerabilities|attack|exploit|secure",
                r"authentication|authorization|validation|sanitization"
            ],
            QueryType.PATTERN_DISCOVERY: [
                r"patterns|design patterns|architecture|architectural",
                r"structure|organization|conventions|standards"
            ],
            QueryType.DEPENDENCY_ANALYSIS: [
                r"depends|dependencies|imports|requires|relationships",
                r"coupling|cohesion|modules|packages"
            ]
        }
        
        # Focus area extraction patterns
        self.focus_patterns = {
            "authentication": r"auth|login|session|token|credential|password",
            "authorization": r"permission|role|access|privilege|security|acl",
            "database": r"database|db|sql|query|model|orm|schema",
            "api": r"api|endpoint|route|controller|service|rest|graphql",
            "ui": r"ui|interface|component|view|template|frontend",
            "testing": r"test|spec|mock|fixture|assertion|coverage",
            "configuration": r"config|setting|environment|env|parameter",
            "logging": r"log|logging|audit|monitoring|debug|trace",
            "error_handling": r"error|exception|failure|fault|handling",
            "performance": r"performance|optimization|speed|memory|cache",
            "security": r"security|vulnerability|encryption|crypto|hash"
        }
    
    def from_natural_language(self, query_text: str, **kwargs) -> SemanticQuery:
        """
        Convert natural language query to semantic query object.
        
        Args:
            query_text: Natural language query from AI agent
            **kwargs: Additional query parameters
            
        Returns:
            Structured semantic query
        """
        query_text_lower = query_text.lower()
        
        # Determine query type from intent patterns
        query_type = self._detect_query_type(query_text_lower)
        
        # Extract focus areas
        focus_areas = self._extract_focus_areas(query_text_lower)
        
        # Extract constraints from query text
        constraints = self._extract_constraints(query_text_lower)
        constraints.update(kwargs.get('constraints', {}))
        
        # Build semantic query
        query = SemanticQuery(
            query_type=query_type,
            intent=query_text,
            focus_areas=focus_areas,
            constraints=constraints,
            context=self._build_query_context(query_text_lower),
            max_tokens=kwargs.get('max_tokens', self.agent_context.token_budget),
            preferred_format=kwargs.get('format', self.agent_context.response_format),
            detail_level=kwargs.get('detail_level', self.agent_context.preferred_detail_level)
        )
        
        return query
    
    def _detect_query_type(self, query_text: str) -> QueryType:
        """Detect query type from natural language patterns."""
        scores = {}
        
        for query_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_text))
                score += matches
            scores[query_type] = score
        
        # Return type with highest score, default to exploration
        if max(scores.values()) == 0:
            return QueryType.EXPLORATION
        
        return max(scores, key=scores.get)
    
    def _extract_focus_areas(self, query_text: str) -> List[str]:
        """Extract focus areas from natural language query."""
        focus_areas = []
        
        for area, pattern in self.focus_patterns.items():
            if re.search(pattern, query_text):
                focus_areas.append(area)
        
        return focus_areas
    
    def _extract_constraints(self, query_text: str) -> Dict[str, Any]:
        """Extract constraints from natural language query."""
        constraints = {}
        
        # File type constraints
        if re.search(r"\.py|python", query_text):
            constraints["file_types"] = ["python"]
        elif re.search(r"\.js|\.ts|javascript|typescript", query_text):
            constraints["file_types"] = ["javascript", "typescript"]
        
        # Complexity constraints
        if re.search(r"high complexity|complex", query_text):
            constraints["min_complexity"] = 10
        elif re.search(r"simple|low complexity", query_text):
            constraints["max_complexity"] = 5
        
        # Size constraints
        if re.search(r"large|big", query_text):
            constraints["min_size"] = 100  # LOC
        elif re.search(r"small|tiny", query_text):
            constraints["max_size"] = 50   # LOC
        
        # Recent changes
        if re.search(r"recent|new|changed|modified", query_text):
            constraints["recent_changes"] = True
        
        return constraints
    
    def _build_query_context(self, query_text: str) -> Dict[str, Any]:
        """Build query context from agent and repository information."""
        # Handle both enum and string values for task
        agent_task = None
        if self.agent_context.task:
            if hasattr(self.agent_context.task, 'value'):
                agent_task = self.agent_context.task.value
            else:
                agent_task = str(self.agent_context.task)
        
        return {
            "agent_task": agent_task,
            "agent_expertise": self.agent_context.expertise_level,
            "repo_size": self.repo_overview.get("estimated_size"),
            "repo_frameworks": self.repo_overview.get("framework_hints", []),
            "query_urgency": "high" if any(word in query_text for word in ["urgent", "critical", "important"]) else "normal"
        }
    
    def create_exploration_query(self, focus_area: Optional[str] = None) -> SemanticQuery:
        """Create exploration query for autonomous codebase navigation."""
        intent = f"Explore codebase architecture and structure"
        if focus_area:
            intent += f" with focus on {focus_area}"
        
        return SemanticQuery(
            query_type=QueryType.EXPLORATION,
            intent=intent,
            focus_areas=[focus_area] if focus_area else [],
            context={"autonomous_exploration": True},
            detail_level="medium",
            preferred_format="structured"
        )
    
    def create_focused_query(self, files: List[str], analysis_type: str) -> SemanticQuery:
        """Create focused analysis query for specific files."""
        return SemanticQuery(
            query_type=QueryType.FOCUSED_ANALYSIS,
            intent=f"Analyze specific files for {analysis_type}",
            constraints={"target_files": files},
            context={"analysis_scope": "focused"},
            detail_level="full",
            preferred_format="structured"
        )
    
    def create_navigation_query(self, concept: str) -> SemanticQuery:
        """Create navigation query to find implementation of concept."""
        return SemanticQuery(
            query_type=QueryType.NAVIGATION,
            intent=f"Navigate to implementation of {concept}",
            focus_areas=self._extract_focus_areas(concept.lower()),
            related_concepts=[concept],
            context={"navigation_target": concept},
            detail_level="medium",
            preferred_format="structured"
        )
    
    def create_impact_query(self, proposed_changes: List[str]) -> SemanticQuery:
        """Create impact analysis query for proposed changes."""
        return SemanticQuery(
            query_type=QueryType.IMPACT_ANALYSIS,
            intent=f"Analyze impact of proposed changes",
            constraints={"change_targets": proposed_changes},
            context={"change_analysis": True},
            detail_level="full",
            preferred_format="structured"
        )
    
    def optimize_for_token_budget(self, query: SemanticQuery, available_tokens: int) -> SemanticQuery:
        """Optimize query for available token budget."""
        if available_tokens < 5000:
            query.detail_level = "minimal"
            query.max_tokens = available_tokens - 1000  # Reserve tokens for processing
        elif available_tokens < 20000:
            query.detail_level = "medium"
            query.max_tokens = available_tokens - 2000
        else:
            query.detail_level = "adaptive"
            query.max_tokens = available_tokens - 3000
        
        return query