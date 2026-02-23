"""IntentGraph - AI-Native Codebase Intelligence Platform."""

from __future__ import annotations

__version__ = "0.5.1"
__author__ = "Nicolas Ligas"
__email__ = "nligas@gmail.com"

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

_lazy_map: dict[str, str] = {
    "AnalysisResult": "intentgraph.domain.models",
    "FileInfo": "intentgraph.domain.models",
    "Language": "intentgraph.domain.models",
    "LanguageSummary": "intentgraph.domain.models",
    "RepositoryAnalyzer": "intentgraph.application.analyzer",
    "connect_to_codebase": "intentgraph.ai",
    "CodebaseAgent": "intentgraph.ai",
    "get_capabilities_manifest": "intentgraph.ai",
}


def __getattr__(name: str) -> object:
    if name in _lazy_map:
        import importlib
        module = importlib.import_module(_lazy_map[name])
        return getattr(module, name)
    raise AttributeError(f"module 'intentgraph' has no attribute {name!r}")


# Convenience functions for quick AI agent integration
def analyze_for_ai(repo_path: str, agent_context: dict = None) -> dict:
    """
    Quick analysis function optimized for AI agents.

    Example:
        >>> results = analyze_for_ai("/path/to/repo", {"task": "bug_fixing"})
        >>> print(results["summary"])
    """
    from .ai import connect_to_codebase
    agent = connect_to_codebase(repo_path, agent_context or {})
    return agent.query("Provide comprehensive codebase analysis")


def quick_explore(repo_path: str, focus_area: str = None) -> dict:
    """
    Quick exploration function for AI agents.

    Example:
        >>> exploration = quick_explore("/path/to/repo", "security")
        >>> print(exploration["findings"])
    """
    from .ai import connect_to_codebase
    agent = connect_to_codebase(repo_path, {"task": "code_understanding"})
    return agent.explore(focus_area)
