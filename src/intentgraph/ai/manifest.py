"""
Self-describing capabilities manifest for AI agent discovery.

This module provides autonomous AI agents with machine-readable information
about IntentGraph's capabilities, enabling automatic discovery and utilization
without human documentation or manual configuration.
"""

from typing import Dict, Any, List
from datetime import datetime
import json

from ..domain.models import Language


def get_capabilities_manifest(repo_overview: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate self-describing capabilities manifest for AI agents.
    
    This manifest allows AI agents to autonomously discover what IntentGraph
    can do and how to use it effectively for their specific tasks.
    
    Args:
        repo_overview: Optional repository overview for context-specific capabilities
        
    Returns:
        Machine-readable capabilities manifest
    """
    
    base_manifest = {
        "intentgraph_ai_interface": {
            "version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "description": "AI-native interface for autonomous codebase intelligence",
            "interface_type": "ai_to_ai"
        },
        
        "capabilities": {
            "analysis_types": {
                "structural_analysis": {
                    "description": "Analyze code structure, dependencies, and architecture",
                    "supports": ["function_dependencies", "class_hierarchies", "module_relationships"],
                    "output_formats": ["minimal", "medium", "full"],
                    "typical_token_cost": "2000-15000"
                },
                "semantic_analysis": {
                    "description": "Extract semantic meaning, patterns, and purposes",
                    "supports": ["design_patterns", "code_purposes", "architectural_layers"],
                    "output_formats": ["structured", "narrative"],
                    "typical_token_cost": "3000-20000"
                },
                "quality_analysis": {
                    "description": "Assess code quality, complexity, and maintainability",
                    "supports": ["complexity_scores", "maintainability_index", "hotspot_detection"],
                    "output_formats": ["metrics", "recommendations"],
                    "typical_token_cost": "1000-8000"
                },
                "intelligent_clustering": {
                    "description": "Break large codebases into navigable clusters",
                    "supports": ["dependency_clustering", "feature_clustering", "size_optimization"],
                    "output_formats": ["cluster_index", "cluster_files"],
                    "typical_token_cost": "5000-50000"
                }
            },
            
            "query_interface": {
                "natural_language": {
                    "description": "Accept queries in natural language",
                    "examples": [
                        "Find files with high complexity",
                        "Show me the API endpoints", 
                        "What are the security vulnerabilities?",
                        "Analyze the authentication system"
                    ],
                    "processing": "automatic_semantic_parsing"
                },
                "semantic_queries": {
                    "description": "Structured semantic query objects",
                    "supports": ["task_aware", "token_budget_aware", "context_sensitive"],
                    "optimization": "automatic"
                },
                "focused_analysis": {
                    "description": "Deep dive analysis on specific files or components",
                    "supports": ["file_lists", "component_names", "concept_search"],
                    "optimization": "context_aware"
                }
            },
            
            "autonomous_features": {
                "capability_discovery": {
                    "description": "Agent can discover what it can do without human docs",
                    "method": "self_describing_manifest"
                },
                "intelligent_navigation": {
                    "description": "AI agent gets guided navigation through codebase",
                    "features": ["recommendation_engine", "next_actions", "impact_analysis"]
                },
                "token_budget_management": {
                    "description": "Automatic response optimization for token limits",
                    "features": ["adaptive_detail", "smart_truncation", "priority_ranking"]
                },
                "context_awareness": {
                    "description": "Responses adapt to agent task and expertise level",
                    "factors": ["agent_task", "token_budget", "expertise_level", "response_format"]
                }
            }
        },
        
        "supported_languages": {
            lang.value: {
                "status": "full" if lang == Language.PYTHON else "basic",
                "features": _get_language_features(lang)
            }
            for lang in Language
        },
        
        "agent_interaction_patterns": {
            "task_based_optimization": {
                "bug_fixing": {
                    "recommended_queries": [
                        "Find high complexity files",
                        "Analyze error handling patterns",
                        "Show recent changes with high risk"
                    ],
                    "optimal_clustering": "analysis_mode",
                    "response_focus": "problematic_areas"
                },
                "feature_development": {
                    "recommended_queries": [
                        "Show extension points",
                        "Analyze similar features",
                        "Find relevant interfaces"
                    ],
                    "optimal_clustering": "refactoring_mode", 
                    "response_focus": "extensibility_patterns"
                },
                "code_review": {
                    "recommended_queries": [
                        "Analyze quality metrics",
                        "Find design pattern violations",
                        "Show dependency risks"
                    ],
                    "optimal_clustering": "analysis_mode",
                    "response_focus": "quality_assessment"
                },
                "security_audit": {
                    "recommended_queries": [
                        "Find input validation patterns",
                        "Analyze authentication flows", 
                        "Show data access paths"
                    ],
                    "optimal_clustering": "feature_based",
                    "response_focus": "security_patterns"
                }
            },
            
            "token_budget_strategies": {
                "small_budget_5k": {
                    "strategy": "focused_minimal_responses",
                    "recommended_approach": "single_concept_queries",
                    "clustering": "disabled"
                },
                "medium_budget_20k": {
                    "strategy": "balanced_detail_responses", 
                    "recommended_approach": "component_based_queries",
                    "clustering": "selective"
                },
                "large_budget_50k": {
                    "strategy": "comprehensive_responses",
                    "recommended_approach": "full_analysis_queries", 
                    "clustering": "enabled"
                }
            }
        },
        
        "usage_examples": {
            "autonomous_bug_fixing": {
                "description": "AI agent autonomously finds and analyzes bugs",
                "code_example": '''
# Autonomous bug fixing workflow
agent = connect_to_codebase("/path/to/repo", {
    "task": "bug_fixing",
    "token_budget": 30000
})

# Agent discovers high-risk areas
issues = agent.query("Find files with high complexity and recent changes")

# Agent analyzes specific problematic areas  
for issue in issues["high_priority"]:
    analysis = agent.get_focused_analysis(issue["files"], "bug_analysis")
    
# Agent gets recommendations for next steps
next_actions = agent.recommend_next_actions(analysis)
                '''.strip()
            },
            
            "autonomous_feature_development": {
                "description": "AI agent analyzes codebase for feature development",
                "code_example": '''
# Feature development workflow
agent = connect_to_codebase("/path/to/repo", {
    "task": "feature_development", 
    "token_budget": 50000
})

# Agent finds similar features for pattern learning
similar = agent.navigate_to_implementation("user authentication")

# Agent analyzes impact of proposed changes
impact = agent.analyze_impact(["src/auth/", "src/api/"])

# Agent explores extension points
extensions = agent.explore("authentication_extensions")
                '''.strip()
            }
        }
    }
    
    # Add repository-specific context if provided
    if repo_overview:
        base_manifest["repository_context"] = {
            "detected_frameworks": repo_overview.get("framework_hints", []),
            "estimated_size": repo_overview.get("estimated_size", "unknown"),
            "file_counts": {
                "python": repo_overview.get("total_python_files", 0),
                "javascript": repo_overview.get("total_js_files", 0)
            },
            "recommended_strategies": _get_recommended_strategies(repo_overview)
        }
    
    return base_manifest


def _get_language_features(language: Language) -> Dict[str, Any]:
    """Get features available for specific language."""
    if language == Language.PYTHON:
        return {
            "symbol_analysis": True,
            "dependency_tracking": True,
            "complexity_metrics": True,
            "design_patterns": True,
            "quality_assessment": True
        }
    else:
        return {
            "symbol_analysis": False,
            "dependency_tracking": True,
            "complexity_metrics": False,
            "design_patterns": False,
            "quality_assessment": False
        }


def _get_recommended_strategies(repo_overview: Dict[str, Any]) -> Dict[str, str]:
    """Get recommended strategies based on repository characteristics."""
    strategies = {}
    
    size = repo_overview.get("estimated_size", "unknown")
    if size == "small":
        strategies["analysis_approach"] = "full_analysis_single_pass"
        strategies["clustering"] = "optional"
        strategies["token_budget"] = "15000_sufficient"
    elif size == "medium":
        strategies["analysis_approach"] = "tiered_analysis_medium_then_focused"
        strategies["clustering"] = "recommended"
        strategies["token_budget"] = "30000_recommended"
    elif size == "large":
        strategies["analysis_approach"] = "clustering_first_then_navigation"
        strategies["clustering"] = "required"
        strategies["token_budget"] = "50000_minimum"
    
    frameworks = repo_overview.get("framework_hints", [])
    if "Django" in frameworks:
        strategies["framework_focus"] = "django_patterns"
    elif "Flask" in frameworks:
        strategies["framework_focus"] = "flask_patterns"
    elif "React" in frameworks:
        strategies["framework_focus"] = "react_patterns"
    
    return strategies


def save_manifest_for_agents(repo_path: str, manifest: Dict[str, Any]) -> str:
    """
    Save capabilities manifest to repository for agent discovery.
    
    Args:
        repo_path: Repository path
        manifest: Capabilities manifest
        
    Returns:
        Path to saved manifest file
    """
    manifest_path = f"{repo_path}/.intentgraph/capabilities_manifest.json"
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return manifest_path


def load_manifest_for_agents(repo_path: str) -> Dict[str, Any]:
    """
    Load existing capabilities manifest for agents.
    
    Args:
        repo_path: Repository path
        
    Returns:
        Loaded capabilities manifest or default if not found
    """
    manifest_path = f"{repo_path}/.intentgraph/capabilities_manifest.json"
    
    try:
        with open(manifest_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return get_capabilities_manifest()