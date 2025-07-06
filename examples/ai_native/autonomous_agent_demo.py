#!/usr/bin/env python3
"""
Autonomous AI Agent Demo - IntentGraph AI-Native Interface

This example demonstrates how AI agents can autonomously analyze and understand
codebases using IntentGraph's AI-native interface without requiring human
intervention or manual command construction.
"""

import json
from pathlib import Path
import sys

# Import AI-native interface
from intentgraph import connect_to_codebase, get_capabilities_manifest, analyze_for_ai, quick_explore


def demonstrate_autonomous_discovery():
    """Demonstrate how AI agents discover IntentGraph capabilities autonomously."""
    print("🤖 AI Agent Autonomous Capability Discovery")
    print("=" * 50)
    
    # AI agent discovers capabilities without human documentation
    capabilities = get_capabilities_manifest()
    
    print("📋 Available Capabilities:")
    for capability, details in capabilities["capabilities"]["analysis_types"].items():
        print(f"  • {capability}: {details['description']}")
        print(f"    Token cost: {details['typical_token_cost']}")
    
    print(f"\n🔍 Query Interface Types:")
    for interface_type, details in capabilities["capabilities"]["query_interface"].items():
        print(f"  • {interface_type}: {details['description']}")
    
    print(f"\n🧠 Autonomous Features:")
    for feature, details in capabilities["capabilities"]["autonomous_features"].items():
        print(f"  • {feature}: {details['description']}")
    
    return capabilities


def demonstrate_natural_language_queries(repo_path: str):
    """Demonstrate natural language query interface for AI agents."""
    print(f"\n🤖 Natural Language Query Interface")
    print("=" * 50)
    
    # Connect to codebase with agent context
    agent = connect_to_codebase(repo_path, {
        "task": "code_understanding",
        "token_budget": 30000,
        "agent_type": "code_reviewer"
    })
    
    # Natural language queries that AI agents can make
    queries = [
        "Find files with high complexity",
        "Show me the main architectural components", 
        "What are the security patterns in this codebase?",
        "Analyze the testing infrastructure"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        try:
            results = agent.query(query)
            
            print(f"   Strategy: {results.get('strategy', 'unknown')}")
            print(f"   Confidence: {results.get('confidence', 'unknown')}")
            print(f"   Files analyzed: {results.get('results', {}).get('file_count', 0)}")
            
            # Show navigation guidance
            navigation = results.get("_navigation", {})
            if navigation.get("next_recommended_queries"):
                print(f"   Next queries: {', '.join(navigation['next_recommended_queries'][:2])}")
            
        except Exception as e:
            print(f"   Error: {e}")


def demonstrate_task_aware_optimization(repo_path: str):
    """Demonstrate how responses adapt to different AI agent tasks."""
    print(f"\n🎯 Task-Aware Response Optimization")
    print("=" * 50)
    
    # Different AI agent tasks
    agent_scenarios = [
        {
            "name": "Bug Fixing Agent",
            "context": {
                "task": "bug_fixing",
                "token_budget": 20000,
                "expertise_level": "expert"
            },
            "query": "Find potential problem areas"
        },
        {
            "name": "Feature Development Agent", 
            "context": {
                "task": "feature_development",
                "token_budget": 40000,
                "expertise_level": "intermediate"
            },
            "query": "Show extension points for new features"
        },
        {
            "name": "Security Audit Agent",
            "context": {
                "task": "security_audit", 
                "token_budget": 15000,
                "expertise_level": "expert"
            },
            "query": "Analyze security patterns and vulnerabilities"
        }
    ]
    
    for scenario in agent_scenarios:
        print(f"\n🤖 {scenario['name']}:")
        
        agent = connect_to_codebase(repo_path, scenario["context"])
        
        try:
            results = agent.query(scenario["query"])
            
            # Show how response is optimized for this agent type
            metadata = results.get("_metadata", {})
            optimization = metadata.get("response_optimization", {})
            
            print(f"   Optimization level: {optimization.get('optimization_level', 'unknown')}")
            print(f"   Token efficiency: {metadata.get('agent_guidance', {}).get('token_efficiency', 'unknown')}")
            print(f"   Completeness: {optimization.get('completeness_score', 'unknown')}")
            
            # Show task-specific recommendations
            if hasattr(agent, 'recommend_next_actions'):
                recommendations = agent.recommend_next_actions()
                if recommendations:
                    print(f"   Recommended action: {recommendations[0].get('action', 'none')}")
            
        except Exception as e:
            print(f"   Error: {e}")


def demonstrate_autonomous_navigation(repo_path: str):
    """Demonstrate autonomous navigation without human guidance."""
    print(f"\n🧭 Autonomous Navigation Demo")
    print("=" * 50)
    
    # AI agent starts exploration autonomously
    agent = connect_to_codebase(repo_path, {
        "task": "code_understanding",
        "token_budget": 50000
    })
    
    print("🔍 Starting autonomous exploration...")
    
    try:
        # Step 1: Autonomous exploration
        exploration = agent.explore()
        print(f"   Exploration strategy: {exploration.get('strategy', 'unknown')}")
        print(f"   Areas discovered: {len(exploration.get('results', {}).get('files', []))}")
        
        # Step 2: Agent gets autonomous recommendations
        recommendations = agent.recommend_next_actions(exploration)
        if recommendations:
            print(f"   Next action recommended: {recommendations[0].get('action', 'none')}")
            
            # Step 3: Agent follows recommendation autonomously
            next_query = recommendations[0].get('query', 'Analyze code quality')
            print(f"   Following up with: '{next_query}'")
            
            follow_up = agent.query(next_query)
            print(f"   Follow-up completed: {follow_up.get('confidence', 'unknown')} confidence")
        
        # Step 4: Token budget management
        remaining_budget = agent.get_token_budget_remaining()
        print(f"   Token budget remaining: {remaining_budget}")
        
        if remaining_budget < 10000:
            print("   🔄 Agent automatically optimizing for remaining budget...")
            agent.set_token_budget(remaining_budget)
            
    except Exception as e:
        print(f"   Navigation error: {e}")


def demonstrate_intelligent_clustering(repo_path: str):
    """Demonstrate intelligent clustering for large codebase navigation."""
    print(f"\n🧩 Intelligent Clustering for Large Codebases")
    print("=" * 50)
    
    # Simulate large codebase scenario
    agent = connect_to_codebase(repo_path, {
        "task": "feature_development",
        "token_budget": 30000
    })
    
    try:
        # AI agent automatically uses clustering for large repos
        cluster_query = "Navigate to authentication implementation"
        results = agent.navigate_to_implementation("authentication")
        
        print(f"   Navigation strategy: {results.get('strategy', 'unknown')}")
        print(f"   Scope: {results.get('scope', 'unknown')}")
        
        if results.get("strategy") == "cluster_navigation":
            cluster_overview = results.get("cluster_overview", {})
            print(f"   Total clusters: {cluster_overview.get('total_clusters', 0)}")
            print(f"   Relevant clusters: {len(results.get('relevant_clusters', []))}")
            
            # Show cluster recommendations
            recommendations = cluster_overview.get("cluster_recommendations", {})
            if recommendations:
                print(f"   AI recommendations available for: {', '.join(recommendations.keys())}")
        
    except Exception as e:
        print(f"   Clustering error: {e}")


def demonstrate_manifest_driven_interaction(repo_path: str):
    """Demonstrate how AI agents use manifest for autonomous interaction."""
    print(f"\n📋 Manifest-Driven Autonomous Interaction")
    print("=" * 50)
    
    # AI agent reads capabilities manifest
    capabilities = get_capabilities_manifest()
    
    # Agent understands available interaction patterns
    interaction_patterns = capabilities.get("agent_interaction_patterns", {})
    task_patterns = interaction_patterns.get("task_based_optimization", {})
    
    print("🤖 Agent discovers available interaction patterns:")
    for task, pattern in task_patterns.items():
        print(f"   {task}: {pattern.get('response_focus', 'unknown')}")
    
    # Agent selects optimal strategy based on manifest
    if "bug_fixing" in task_patterns:
        print(f"\n🔍 Agent selects bug_fixing strategy:")
        bug_pattern = task_patterns["bug_fixing"]
        
        recommended_queries = bug_pattern.get("recommended_queries", [])
        optimal_clustering = bug_pattern.get("optimal_clustering", "none")
        
        print(f"   Recommended queries: {recommended_queries}")
        print(f"   Optimal clustering: {optimal_clustering}")
        
        # Agent executes based on manifest guidance
        agent = connect_to_codebase(repo_path, {"task": "bug_fixing"})
        
        if recommended_queries:
            try:
                results = agent.query(recommended_queries[0])
                print(f"   Query executed: ✅ Success")
                print(f"   Results confidence: {results.get('confidence', 'unknown')}")
            except Exception as e:
                print(f"   Query error: {e}")


def demonstrate_quick_ai_functions(repo_path: str):
    """Demonstrate quick AI functions for rapid integration."""
    print(f"\n⚡ Quick AI Functions for Rapid Integration")
    print("=" * 50)
    
    try:
        # Quick analysis for AI agents
        print("🔍 Quick AI analysis...")
        analysis = analyze_for_ai(repo_path, {"task": "code_review"})
        
        if analysis:
            query_response = analysis.get("query_response", {})
            print(f"   Analysis type: {query_response.get('query_type', 'unknown')}")
            print(f"   Confidence: {query_response.get('confidence', 'unknown')}")
            
            findings = analysis.get("findings", {})
            print(f"   Files analyzed: {findings.get('file_count', 0)}")
        
        # Quick exploration
        print(f"\n🗺️ Quick exploration...")
        exploration = quick_explore(repo_path, "security")
        
        if exploration:
            print(f"   Exploration scope: {exploration.get('scope', 'unknown')}")
            print(f"   Strategy used: {exploration.get('strategy', 'unknown')}")
        
    except Exception as e:
        print(f"   Quick functions error: {e}")


def main():
    """Main demonstration function."""
    if len(sys.argv) < 2:
        print("Usage: python autonomous_agent_demo.py <repository_path>")
        print("Example: python autonomous_agent_demo.py /path/to/your/repository")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    
    print("🚀 IntentGraph AI-Native Interface Demo")
    print("=" * 60)
    print(f"Repository: {repo_path}")
    print("Demonstrating autonomous AI agent capabilities...")
    
    try:
        # 1. Autonomous capability discovery
        demonstrate_autonomous_discovery()
        
        # 2. Natural language queries  
        demonstrate_natural_language_queries(repo_path)
        
        # 3. Task-aware optimization
        demonstrate_task_aware_optimization(repo_path)
        
        # 4. Autonomous navigation
        demonstrate_autonomous_navigation(repo_path)
        
        # 5. Intelligent clustering
        demonstrate_intelligent_clustering(repo_path)
        
        # 6. Manifest-driven interaction
        demonstrate_manifest_driven_interaction(repo_path)
        
        # 7. Quick AI functions
        demonstrate_quick_ai_functions(repo_path)
        
        print(f"\n✨ Demo Complete!")
        print("🤖 AI agents can now autonomously analyze and understand codebases")
        print("   without requiring human intervention or manual commands!")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()