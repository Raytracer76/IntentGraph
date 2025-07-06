#!/usr/bin/env python3
"""
Simple test to verify AI-native interface is working correctly.
"""

def test_ai_interface():
    """Test basic AI interface functionality."""
    print("🧪 Testing AI-Native Interface")
    print("=" * 40)
    
    try:
        # Test 1: Import AI interface
        print("1. Testing imports...")
        from src.intentgraph.ai import connect_to_codebase, get_capabilities_manifest
        from src.intentgraph import analyze_for_ai, quick_explore
        print("   ✅ All imports successful")
        
        # Test 2: Capabilities manifest
        print("\n2. Testing capabilities manifest...")
        manifest = get_capabilities_manifest()
        
        required_keys = ["intentgraph_ai_interface", "capabilities", "supported_languages"]
        for key in required_keys:
            assert key in manifest, f"Missing key: {key}"
        
        print(f"   ✅ Manifest contains {len(manifest)} sections")
        print(f"   ✅ Analysis types: {len(manifest['capabilities']['analysis_types'])}")
        
        # Test 3: Basic query building
        print("\n3. Testing query interface...")
        from src.intentgraph.ai.query import QueryBuilder, SemanticQuery
        from src.intentgraph.ai.agent import AgentContext
        
        context = AgentContext(agent_type="test", task="bug_fixing")
        builder = QueryBuilder(context, {"estimated_size": "small"})
        
        query = builder.from_natural_language("Find high complexity files")
        assert query.intent == "Find high complexity files"
        assert query.query_type is not None
        
        print("   ✅ Query building works correctly")
        
        # Test 4: Response optimization
        print("\n4. Testing response optimization...")
        from src.intentgraph.ai.response import ResponseOptimizer, TokenBudget
        
        budget = TokenBudget(total=10000)
        optimizer = ResponseOptimizer(context, budget)
        
        # Test budget management
        assert budget.remaining() == 9000  # 10000 - 1000 reserved
        assert budget.can_afford(5000) == True
        assert budget.can_afford(15000) == False
        
        print("   ✅ Response optimization works correctly")
        
        # Test 5: Navigation system
        print("\n5. Testing navigation system...")
        from src.intentgraph.ai.navigation import AutonomousNavigator, NavigationContext
        from pathlib import Path
        
        nav_context = NavigationContext()
        assert nav_context.token_budget_remaining == 50000
        
        print("   ✅ Navigation system initialized correctly")
        
        print("\n🎉 All tests passed! AI-native interface is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_ai_interface()
    exit(0 if success else 1)