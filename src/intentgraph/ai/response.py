"""
Response optimization for AI-native interfaces.

This module optimizes codebase intelligence responses for AI agents based on
token budgets, agent context, and task requirements, ensuring efficient
and relevant information delivery.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json
import re


class ResponseFormat(str, Enum):
    """Response format types for different AI agent needs."""
    STRUCTURED = "structured"         # JSON-like structured data
    NARRATIVE = "narrative"           # Natural language explanations
    CODE_FOCUSED = "code_focused"     # Emphasis on code examples and snippets
    METRICS_FOCUSED = "metrics_focused" # Emphasis on numbers and measurements
    ACTIONABLE = "actionable"         # Focus on next steps and recommendations


@dataclass
class TokenBudget:
    """Token budget management for AI agent responses."""
    
    total: int
    used: int = 0
    reserved: int = 1000  # Reserved for response formatting
    
    def remaining(self) -> int:
        """Get remaining token budget."""
        return max(0, self.total - self.used - self.reserved)
    
    def can_afford(self, cost: int) -> bool:
        """Check if we can afford a response of given token cost."""
        return self.remaining() >= cost
    
    def consume(self, cost: int) -> bool:
        """Consume tokens from budget. Returns True if successful."""
        if self.can_afford(cost):
            self.used += cost
            return True
        return False
    
    def get_budget_tier(self) -> str:
        """Get budget tier for response optimization."""
        remaining = self.remaining()
        if remaining < 2000:
            return "minimal"
        elif remaining < 10000:
            return "conservative" 
        elif remaining < 30000:
            return "balanced"
        else:
            return "comprehensive"


class ResponseOptimizer:
    """
    Intelligent response optimizer that adapts codebase intelligence
    for AI agent needs, token budgets, and task contexts.
    """
    
    def __init__(self, agent_context: 'AgentContext', token_budget: TokenBudget):
        """
        Initialize response optimizer.
        
        Args:
            agent_context: AI agent context information
            token_budget: Available token budget for responses
        """
        self.agent_context = agent_context
        self.token_budget = token_budget
        
        # Content prioritization based on agent task
        self.task_priorities = {
            "bug_fixing": ["complexity_scores", "error_patterns", "recent_changes", "dependencies"],
            "feature_development": ["extension_points", "similar_patterns", "interfaces", "architecture"],
            "code_review": ["quality_metrics", "violations", "complexity", "maintainability"],
            "security_audit": ["input_validation", "authentication", "authorization", "data_flow"],
            "refactoring": ["coupling", "cohesion", "patterns", "dependencies"],
            "documentation": ["public_apis", "interfaces", "architecture", "examples"],
            "testing": ["test_coverage", "testability", "mocks", "fixtures"],
            "performance_optimization": ["hotspots", "complexity", "algorithms", "bottlenecks"]
        }
        
        # Response structure templates
        self.response_templates = {
            ResponseFormat.STRUCTURED: self._structured_template,
            ResponseFormat.NARRATIVE: self._narrative_template,
            ResponseFormat.CODE_FOCUSED: self._code_focused_template,
            ResponseFormat.METRICS_FOCUSED: self._metrics_template,
            ResponseFormat.ACTIONABLE: self._actionable_template
        }
    
    def optimize_response(self, raw_results: Dict[str, Any], query: 'SemanticQuery', 
                         budget: TokenBudget) -> Dict[str, Any]:
        """
        Optimize raw analysis results for AI agent consumption.
        
        Args:
            raw_results: Raw codebase analysis results
            query: Original semantic query
            budget: Current token budget
            
        Returns:
            Optimized response tailored for AI agent
        """
        # Determine response format
        response_format = ResponseFormat(query.preferred_format)
        
        # Get content priorities based on agent task and query
        priorities = self._get_content_priorities(query)
        
        # Filter and rank content by priority
        filtered_content = self._filter_by_priority(raw_results, priorities, budget)
        
        # Apply response template
        template_func = self.response_templates[response_format]
        structured_response = template_func(filtered_content, query, budget)
        
        # Add AI-native metadata
        structured_response["_metadata"] = self._generate_response_metadata(
            query, budget, len(json.dumps(structured_response))
        )
        
        return structured_response
    
    def _get_content_priorities(self, query: 'SemanticQuery') -> List[str]:
        """Get content priorities based on agent task and query type."""
        priorities = []
        
        # Task-based priorities
        if self.agent_context.task and self.agent_context.task.value in self.task_priorities:
            priorities.extend(self.task_priorities[self.agent_context.task.value])
        
        # Query-type specific priorities
        if query.query_type.value == "exploration":
            priorities.extend(["architecture", "overview", "structure"])
        elif query.query_type.value == "focused_analysis":
            priorities.extend(["detailed_metrics", "symbols", "dependencies"])
        elif query.query_type.value == "navigation":
            priorities.extend(["implementations", "interfaces", "related_files"])
        elif query.query_type.value == "impact_analysis":
            priorities.extend(["dependencies", "reverse_dependencies", "coupling"])
        
        # Focus area priorities
        for focus_area in query.focus_areas:
            if focus_area == "security":
                priorities.extend(["input_validation", "authentication", "authorization"])
            elif focus_area == "performance":
                priorities.extend(["complexity", "algorithms", "hotspots"])
            elif focus_area == "testing":
                priorities.extend(["test_coverage", "testability"])
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(priorities))
    
    def _filter_by_priority(self, raw_results: Dict[str, Any], 
                           priorities: List[str], budget: TokenBudget) -> Dict[str, Any]:
        """Filter and rank content based on priorities and token budget."""
        budget_tier = budget.get_budget_tier()
        filtered = {}
        
        # Essential content (always include)
        essential_keys = ["summary", "file_count", "primary_findings"]
        for key in essential_keys:
            if key in raw_results:
                filtered[key] = raw_results[key]
        
        # Priority-based content inclusion
        if budget_tier in ["comprehensive", "balanced"]:
            # Include high-priority content
            for priority in priorities[:5]:  # Top 5 priorities
                if priority in raw_results:
                    filtered[priority] = raw_results[priority]
        
        if budget_tier == "comprehensive":
            # Include additional context
            for priority in priorities[5:10]:  # Next 5 priorities
                if priority in raw_results:
                    filtered[priority] = raw_results[priority]
        
        # Always include recommendations for AI agents
        if "recommendations" in raw_results:
            filtered["recommendations"] = raw_results["recommendations"]
        
        return filtered
    
    def _structured_template(self, content: Dict[str, Any], query: 'SemanticQuery', 
                           budget: TokenBudget) -> Dict[str, Any]:
        """Apply structured response template."""
        return {
            "query_response": {
                "intent": query.intent,
                "query_type": query.query_type.value,
                "confidence": "high"  # Could be calculated based on content match
            },
            "findings": content,
            "navigation": {
                "related_queries": self._generate_related_queries(content, query),
                "next_actions": self._generate_next_actions(content, query),
                "deep_dive_options": self._generate_deep_dive_options(content)
            },
            "token_optimization": {
                "budget_used": budget.used,
                "budget_remaining": budget.remaining(),
                "response_completeness": self._calculate_completeness(content, budget)
            }
        }
    
    def _narrative_template(self, content: Dict[str, Any], query: 'SemanticQuery',
                          budget: TokenBudget) -> Dict[str, Any]:
        """Apply narrative response template."""
        narrative = self._generate_narrative_explanation(content, query)
        
        return {
            "explanation": narrative,
            "key_points": self._extract_key_points(content),
            "detailed_findings": content,
            "follow_up_suggestions": self._generate_follow_up_suggestions(content, query)
        }
    
    def _code_focused_template(self, content: Dict[str, Any], query: 'SemanticQuery',
                             budget: TokenBudget) -> Dict[str, Any]:
        """Apply code-focused response template."""
        return {
            "code_insights": {
                "relevant_files": content.get("files", []),
                "key_functions": content.get("functions", []),
                "code_patterns": content.get("patterns", []),
                "implementation_details": content.get("implementations", [])
            },
            "code_quality": {
                "metrics": content.get("metrics", {}),
                "issues": content.get("issues", []),
                "recommendations": content.get("recommendations", [])
            },
            "code_navigation": {
                "entry_points": content.get("entry_points", []),
                "dependencies": content.get("dependencies", []),
                "related_code": content.get("related_files", [])
            }
        }
    
    def _metrics_template(self, content: Dict[str, Any], query: 'SemanticQuery',
                         budget: TokenBudget) -> Dict[str, Any]:
        """Apply metrics-focused response template."""
        return {
            "quantitative_analysis": {
                "key_metrics": content.get("metrics", {}),
                "quality_scores": content.get("quality", {}),
                "complexity_analysis": content.get("complexity", {}),
                "trend_indicators": content.get("trends", {})
            },
            "comparative_analysis": {
                "benchmarks": content.get("benchmarks", {}),
                "relative_rankings": content.get("rankings", []),
                "improvement_potential": content.get("improvement", {})
            },
            "actionable_metrics": {
                "priority_areas": content.get("priority_areas", []),
                "target_improvements": content.get("targets", {}),
                "success_criteria": content.get("criteria", [])
            }
        }
    
    def _actionable_template(self, content: Dict[str, Any], query: 'SemanticQuery',
                           budget: TokenBudget) -> Dict[str, Any]:
        """Apply actionable response template."""
        return {
            "immediate_actions": self._generate_immediate_actions(content, query),
            "investigation_paths": self._generate_investigation_paths(content, query),
            "implementation_guidance": self._generate_implementation_guidance(content),
            "risk_assessment": self._generate_risk_assessment(content),
            "success_criteria": self._generate_success_criteria(content, query)
        }
    
    def _generate_narrative_explanation(self, content: Dict[str, Any], 
                                      query: 'SemanticQuery') -> str:
        """Generate natural language explanation of findings."""
        # This would use the content to create a narrative explanation
        # For now, return a template-based explanation
        
        intent = query.intent.lower()
        findings_count = len(content.get("files", []))
        
        if "find" in intent:
            return f"Found {findings_count} relevant items matching your query. " \
                   f"The analysis reveals several key patterns and areas of interest."
        elif "analyze" in intent:
            return f"Analysis complete on {findings_count} components. " \
                   f"The codebase shows specific characteristics relevant to your inquiry."
        else:
            return f"Exploration of the codebase identified {findings_count} relevant areas " \
                   f"with insights into the requested aspects."
    
    def _generate_related_queries(self, content: Dict[str, Any], 
                                query: 'SemanticQuery') -> List[str]:
        """Generate related queries that might interest the AI agent."""
        related = []
        
        if query.query_type.value == "exploration":
            related.extend([
                "Analyze code quality metrics",
                "Find potential security issues",
                "Show architectural patterns"
            ])
        elif query.query_type.value == "focused_analysis":
            related.extend([
                "Find similar implementations",
                "Analyze dependencies of these files", 
                "Check for potential improvements"
            ])
        
        return related[:3]  # Limit to 3 suggestions
    
    def _generate_next_actions(self, content: Dict[str, Any], 
                             query: 'SemanticQuery') -> List[Dict[str, str]]:
        """Generate next action recommendations for AI agents."""
        actions = []
        
        if self.agent_context.task:
            task = self.agent_context.task.value
            
            if task == "bug_fixing" and content.get("complexity_scores"):
                actions.append({
                    "action": "focus_on_high_complexity",
                    "description": "Analyze high-complexity files for potential bugs",
                    "priority": "high"
                })
            
            if task == "feature_development" and content.get("interfaces"):
                actions.append({
                    "action": "explore_extension_points", 
                    "description": "Examine interfaces for feature extension opportunities",
                    "priority": "medium"
                })
        
        return actions
    
    def _generate_deep_dive_options(self, content: Dict[str, Any]) -> List[str]:
        """Generate deep dive analysis options."""
        options = []
        
        if content.get("files"):
            options.append("Detailed analysis of specific files")
        
        if content.get("dependencies"):
            options.append("Dependency impact analysis")
        
        if content.get("patterns"):
            options.append("Design pattern analysis")
        
        return options
    
    def _generate_response_metadata(self, query: 'SemanticQuery', budget: TokenBudget,
                                  response_size: int) -> Dict[str, Any]:
        """Generate AI-native metadata for the response."""
        return {
            "response_optimization": {
                "target_tokens": query.max_tokens,
                "actual_tokens": response_size // 4,  # Rough estimate
                "optimization_level": budget.get_budget_tier(),
                "completeness_score": self._calculate_completeness({}, budget)
            },
            "agent_guidance": {
                "confidence_level": "high",
                "recommended_follow_up": True,
                "token_efficiency": "optimal" if budget.remaining() > 5000 else "constrained"
            },
            "query_analysis": {
                "complexity": "medium",
                "scope": query.query_type.value,
                "focus_areas_covered": len(query.focus_areas)
            }
        }
    
    def _calculate_completeness(self, content: Dict[str, Any], budget: TokenBudget) -> float:
        """Calculate response completeness score."""
        # This would calculate how complete the response is given the budget constraints
        # For now, return a simple calculation based on budget tier
        
        tier = budget.get_budget_tier()
        if tier == "comprehensive":
            return 0.95
        elif tier == "balanced":
            return 0.80
        elif tier == "conservative":
            return 0.65
        else:
            return 0.45
    
    def _extract_key_points(self, content: Dict[str, Any]) -> List[str]:
        """Extract key points from content for narrative responses."""
        points = []
        
        if content.get("file_count"):
            points.append(f"Analysis covers {content['file_count']} files")
        
        if content.get("complexity"):
            points.append(f"Average complexity score: {content['complexity']}")
        
        return points
    
    def _generate_follow_up_suggestions(self, content: Dict[str, Any], 
                                      query: 'SemanticQuery') -> List[str]:
        """Generate follow-up suggestions for narrative responses."""
        suggestions = []
        
        if query.query_type.value == "exploration":
            suggestions.append("Consider focusing on specific architectural components")
        
        if content.get("issues"):
            suggestions.append("Investigate identified issues for potential improvements")
        
        return suggestions
    
    def _generate_immediate_actions(self, content: Dict[str, Any], 
                                  query: 'SemanticQuery') -> List[Dict[str, str]]:
        """Generate immediate action items."""
        return [
            {
                "action": "review_findings",
                "description": "Review the identified findings and assess priorities",
                "timeline": "immediate"
            }
        ]
    
    def _generate_investigation_paths(self, content: Dict[str, Any],
                                    query: 'SemanticQuery') -> List[Dict[str, str]]:
        """Generate investigation path suggestions."""
        return [
            {
                "path": "deep_dive_analysis",
                "description": "Perform detailed analysis on specific components",
                "expected_outcome": "Detailed understanding of implementation"
            }
        ]
    
    def _generate_implementation_guidance(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate implementation guidance."""
        return {
            "best_practices": ["Follow established patterns", "Maintain consistency"],
            "considerations": ["Impact on existing code", "Testing requirements"],
            "resources": ["Documentation", "Similar implementations"]
        }
    
    def _generate_risk_assessment(self, content: Dict[str, Any]) -> Dict[str, str]:
        """Generate risk assessment."""
        return {
            "overall_risk": "medium",
            "key_risks": "Complexity in certain areas",
            "mitigation": "Focus on testing and documentation"
        }
    
    def _generate_success_criteria(self, content: Dict[str, Any], 
                                 query: 'SemanticQuery') -> List[str]:
        """Generate success criteria."""
        return [
            "Clear understanding of codebase structure",
            "Identification of key areas for focus",
            "Actionable insights for next steps"
        ]