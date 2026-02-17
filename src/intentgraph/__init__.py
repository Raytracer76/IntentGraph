"""IntentGraph - AI-Native Codebase Intelligence Platform."""

__version__ = "0.4.0"
__author__ = "Nicolas Ligas"
__email__ = "nligas@gmail.com"

# Core domain models
from .domain.models import AnalysisResult, FileInfo, Language, LanguageSummary

# AI-Native Interface - Primary entry point for autonomous agents
from .ai import connect_to_codebase, CodebaseAgent, get_capabilities_manifest

# Traditional programmatic interface
from .application.analyzer import RepositoryAnalyzer

__all__ = [
    # AI-Native Interface (recommended for autonomous agents)
    "connect_to_codebase",
    "CodebaseAgent", 
    "get_capabilities_manifest",
    
    # Traditional Interface (for manual integration)
    "RepositoryAnalyzer",
    "AnalysisResult",
    "FileInfo", 
    "Language",
    "LanguageSummary",
]

# Convenience functions for quick AI agent integration
def analyze_for_ai(repo_path: str, agent_context: dict = None) -> dict:
    """
    Quick analysis function optimized for AI agents.
    
    Args:
        repo_path: Path to repository
        agent_context: Optional agent context
        
    Returns:
        AI-optimized analysis results
        
    Example:
        >>> results = analyze_for_ai("/path/to/repo", {"task": "bug_fixing"})
        >>> print(results["summary"])
    """
    agent = connect_to_codebase(repo_path, agent_context or {})
    return agent.query("Provide comprehensive codebase analysis")

def quick_explore(repo_path: str, focus_area: str = None) -> dict:
    """
    Quick exploration function for AI agents.
    
    Args:
        repo_path: Path to repository
        focus_area: Optional area to focus exploration
        
    Returns:
        Exploration results with navigation guidance
        
    Example:
        >>> exploration = quick_explore("/path/to/repo", "security")
        >>> print(exploration["findings"])
    """
    agent = connect_to_codebase(repo_path, {"task": "code_understanding"})
    return agent.explore(focus_area)
