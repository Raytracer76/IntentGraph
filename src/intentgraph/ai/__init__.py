"""
AI-Native Interface for IntentGraph

This module provides autonomous AI agents with direct, programmatic access to
structured codebase intelligence without requiring human mediation or manual
command construction.

Core Philosophy:
- Agents discover capabilities through self-describing manifests
- Queries are semantic and task-aware, not command-based
- Responses are optimized for token budgets and agent context
- Navigation is autonomous with intelligent recommendations
"""

from .agent import CodebaseAgent
from .manifest import get_capabilities_manifest
from .query import SemanticQuery, QueryBuilder
from .response import ResponseOptimizer, TokenBudget
from .navigation import AutonomousNavigator

__all__ = [
    'CodebaseAgent',
    'get_capabilities_manifest', 
    'SemanticQuery',
    'QueryBuilder',
    'ResponseOptimizer',
    'TokenBudget',
    'AutonomousNavigator'
]

# AI-Native Quick Start for Autonomous Agents
def connect_to_codebase(repo_path: str, agent_context: dict = None) -> 'CodebaseAgent':
    """
    Primary entry point for AI agents to connect to a codebase.
    
    Args:
        repo_path: Path to the repository to analyze
        agent_context: Optional context about the agent's capabilities and goals
        
    Returns:
        CodebaseAgent: Autonomous interface to codebase intelligence
        
    Example:
        >>> agent = connect_to_codebase("/path/to/repo", {
        ...     "task": "bug_fixing",
        ...     "token_budget": 50000,
        ...     "agent_type": "code_reviewer"
        ... })
        >>> results = agent.query("Find files with high complexity in payment logic")
    """
    return CodebaseAgent(repo_path, agent_context or {})