#!/usr/bin/env python3
"""
Quick demonstration of IntentGraph's AI-native interface.
"""

def demonstrate_ai_interface():
    """Demonstrate AI-native interface capabilities."""
    print("🤖 IntentGraph AI-Native Interface Demo")
    print("=" * 50)
    
    try:
        # 1. Import AI interface
        print("1. 🧠 AI Agent Discovery Phase")
        from src.intentgraph.ai import get_capabilities_manifest
        
        # AI agent discovers capabilities autonomously
        capabilities = get_capabilities_manifest()
        
        print("   📋 AI Agent discovers available capabilities:")
        analysis_types = capabilities["capabilities"]["analysis_types"]
        for analysis_type, details in analysis_types.items():
            print(f"      • {analysis_type}: {details['description']}")
        
        print(f"\n   🎯 AI Agent finds {len(capabilities['agent_interaction_patterns']['task_based_optimization'])} task optimization patterns")
        
        # 2. Natural Language Interface
        print("\n2. 🗣️  Natural Language Query Interface")
        from src.intentgraph.ai.query import QueryBuilder
        from src.intentgraph.ai.agent import AgentContext
        
        # AI agent context
        agent_context = AgentContext(
            agent_type="autonomous_code_reviewer",
            task="bug_fixing",
            token_budget=25000,
            expertise_level="expert"
        )
        
        # Repository context
        repo_overview = {
            "estimated_size": "medium",
            "framework_hints": ["Flask", "SQLAlchemy"],
            "total_python_files": 45
        }
        
        # AI agent creates queries using natural language
        builder = QueryBuilder(agent_context, repo_overview)
        
        natural_queries = [
            "Find files with high complexity that might contain bugs",
            "Show me the authentication and security patterns",
            "Analyze the database access patterns for potential issues"
        ]
        
        print("   🔍 AI Agent creates semantic queries:")
        for query_text in natural_queries:
            query = builder.from_natural_language(query_text)
            print(f"      • '{query_text}'")
            print(f"        → Type: {query.query_type.value}")
            print(f"        → Focus: {query.focus_areas}")
            print(f"        → Context: {query.context['agent_task']}")
        
        # 3. Token Budget Management
        print("\n3. 💰 Intelligent Token Budget Management")
        from src.intentgraph.ai.response import TokenBudget, ResponseOptimizer
        
        # Different budget scenarios
        budgets = [
            ("Small Budget (5K tokens)", 5000),
            ("Medium Budget (20K tokens)", 20000), 
            ("Large Budget (50K tokens)", 50000)
        ]
        
        for budget_name, budget_size in budgets:
            budget = TokenBudget(total=budget_size)
            optimizer = ResponseOptimizer(agent_context, budget)
            
            tier = budget.get_budget_tier()
            remaining = budget.remaining()
            
            print(f"   {budget_name}:")
            print(f"      • Budget tier: {tier}")
            print(f"      • Available tokens: {remaining}")
            # Map budget tier to correct strategy key
            strategy_key_map = {
                'minimal': 'minimal_budget_5k',
                'conservative': 'medium_budget_20k', 
                'aggressive': 'large_budget_50k'
            }
            strategy_key = strategy_key_map.get(tier, 'medium_budget_20k')
            strategy = capabilities['agent_interaction_patterns']['token_budget_strategies'][strategy_key]['strategy']
            print(f"      • Strategy: {strategy}")
        
        # 4. Task-Aware Optimization
        print("\n4. 🎯 Task-Aware Response Optimization")
        
        task_scenarios = [
            ("Bug Fixing Agent", "bug_fixing"),
            ("Feature Development Agent", "feature_development"),
            ("Security Audit Agent", "security_audit")
        ]
        
        for agent_name, task_type in task_scenarios:
            task_context = AgentContext(agent_type=agent_name.lower().replace(" ", "_"), task=task_type)
            task_optimizer = ResponseOptimizer(task_context, TokenBudget(30000))
            
            # Get task-specific priorities
            task_patterns = capabilities["agent_interaction_patterns"]["task_based_optimization"]
            if task_type in task_patterns:
                pattern = task_patterns[task_type]
                print(f"   {agent_name}:")
                print(f"      • Focus: {pattern['response_focus']}")
                print(f"      • Clustering: {pattern['optimal_clustering']}")
                print(f"      • Sample query: {pattern['recommended_queries'][0]}")
        
        # 5. Autonomous Navigation
        print("\n5. 🧭 Autonomous Navigation Preview")
        from src.intentgraph.ai.navigation import AutonomousNavigator, NavigationContext
        
        nav_context = NavigationContext(
            agent_goals=["understand_architecture", "find_security_issues"],
            priority_areas=["authentication", "data_access"],
            token_budget_remaining=30000
        )
        
        print("   🤖 AI Agent navigation context:")
        print(f"      • Goals: {', '.join(nav_context.agent_goals)}")
        print(f"      • Priority areas: {', '.join(nav_context.priority_areas)}")
        print(f"      • Budget remaining: {nav_context.token_budget_remaining}")
        
        # 6. Self-Describing Interface
        print("\n6. 📜 Self-Describing Interface Examples")
        
        usage_examples = capabilities["usage_examples"]
        print("   🔧 Available AI agent workflow patterns:")
        for workflow_name, workflow_details in usage_examples.items():
            print(f"      • {workflow_name}: {workflow_details['description']}")
        
        print("\n✨ AI-Native Interface Demonstration Complete!")
        print("\n🚀 Key Capabilities Demonstrated:")
        print("   ✅ Autonomous capability discovery (no human docs needed)")
        print("   ✅ Natural language query interface")
        print("   ✅ Intelligent token budget management")
        print("   ✅ Task-aware response optimization")
        print("   ✅ Autonomous navigation guidance")
        print("   ✅ Self-describing interface with examples")
        
        print("\n🤖 AI agents can now autonomously:")
        print("   • Discover what IntentGraph can do")
        print("   • Query codebases using natural language")
        print("   • Get optimized responses for their specific task")
        print("   • Navigate large codebases intelligently")
        print("   • Manage token budgets automatically")
        print("   • Work without human intervention!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = demonstrate_ai_interface()
    print(f"\n{'🎉 Demo completed successfully!' if success else '❌ Demo failed'}")