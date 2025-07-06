"""Demonstration of IntentGraph AI-optimized output levels."""

import json
import subprocess
from pathlib import Path


def demo_output_levels():
    """Compare all three output levels for AI agent usage."""
    repo_path = Path.cwd()
    
    print("🤖 IntentGraph AI-Optimized Output Levels Demo\n")
    
    # Test all three levels
    levels = ["minimal", "medium", "full"]
    results = {}
    
    for level in levels:
        print(f"Analyzing with --level {level}...")
        
        # Run intentgraph CLI with different levels
        result = subprocess.run([
            "intentgraph", str(repo_path), 
            "--level", level,
            "--format", "compact"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Parse JSON output and get size
            analysis = json.loads(result.stdout)
            size_kb = len(result.stdout.encode('utf-8')) / 1024
            
            results[level] = {
                "size_kb": round(size_kb, 1),
                "files_count": len(analysis.get("files", [])),
                "analysis": analysis
            }
            
            print(f"  ✅ Size: {size_kb:.1f}KB")
            print(f"  📁 Files: {len(analysis.get('files', []))}")
        else:
            print(f"  ❌ Error: {result.stderr}")
    
    print(f"\n📊 Size Comparison:")
    for level, data in results.items():
        print(f"  {level:8s}: {data['size_kb']:6.1f}KB")
    
    return results


def analyze_ai_suitability():
    """Analyze which level is best for different AI use cases."""
    print("\n🎯 AI Use Case Recommendations:")
    
    use_cases = {
        "Quick code understanding": "minimal",
        "Function dependency analysis": "minimal", 
        "Code review assistance": "medium",
        "Refactoring planning": "medium",
        "Comprehensive auditing": "full",
        "Architecture documentation": "full"
    }
    
    for use_case, recommended_level in use_cases.items():
        print(f"  {use_case:25s} → --level {recommended_level}")


def demonstrate_content_differences():
    """Show what content is included at each level."""
    print("\n📋 Content Included by Level:")
    
    content_by_level = {
        "minimal": [
            "✓ File paths and languages",
            "✓ Import statements", 
            "✓ File dependencies",
            "✓ Basic metrics (LOC, complexity)",
            "❌ Symbol details",
            "❌ Function signatures",
            "❌ Docstrings"
        ],
        "medium": [
            "✓ Everything from minimal",
            "✓ Key symbols (classes, public functions)",
            "✓ Export information",
            "✓ Maintainability scores",
            "✓ File purpose inference",
            "❌ Complete symbol metadata",
            "❌ Implementation details"
        ],
        "full": [
            "✓ Everything from medium",
            "✓ Complete symbol metadata",
            "✓ Function signatures and docstrings",
            "✓ Design pattern detection",
            "✓ Function-level dependencies",
            "✓ All analysis metadata"
        ]
    }
    
    for level, content in content_by_level.items():
        print(f"\n  {level.upper()}:")
        for item in content:
            print(f"    {item}")


def ai_token_limit_analysis():
    """Analyze how output levels fit within AI token limits."""
    print("\n🤖 AI Token Limit Analysis:")
    
    # Common AI model token limits (approximate)
    token_limits = {
        "GPT-3.5-turbo": "4K tokens (~16KB)",
        "GPT-4": "8K tokens (~32KB)", 
        "GPT-4-turbo": "128K tokens (~512KB)",
        "Claude-3": "200K tokens (~800KB)",
        "Gemini-Pro": "32K tokens (~128KB)"
    }
    
    level_sizes = {
        "minimal": 10.7,  # KB
        "medium": 69,     # KB  
        "full": 337       # KB
    }
    
    print("  Model Compatibility:")
    for model, limit in token_limits.items():
        print(f"\n  {model}:")
        for level, size in level_sizes.items():
            # Rough conversion: 1KB ≈ 250 tokens
            estimated_tokens = size * 250
            
            if "4K" in limit and estimated_tokens < 4000:
                status = "✅"
            elif "8K" in limit and estimated_tokens < 8000:
                status = "✅"
            elif "32K" in limit and estimated_tokens < 32000:
                status = "✅" 
            elif "128K" in limit and estimated_tokens < 128000:
                status = "✅"
            elif "200K" in limit and estimated_tokens < 200000:
                status = "✅"
            else:
                status = "❌"
            
            print(f"    {level:8s}: {size:6.1f}KB (~{estimated_tokens:5.0f} tokens) {status}")


def example_ai_agent_usage():
    """Show example code for AI agents using different levels."""
    print("\n💻 Example AI Agent Usage:")
    
    examples = {
        "minimal": '''
# Perfect for initial codebase understanding
analysis = subprocess.run(["intentgraph", ".", "--level", "minimal"], 
                         capture_output=True, text=True)
data = json.loads(analysis.stdout)

# Quick overview for AI agent
print(f"Repository has {len(data['files'])} files")
for file in data['files']:
    print(f"  {file['path']}: {len(file['imports'])} imports")
''',
        
        "medium": '''
# Ideal for code review and refactoring planning
analysis = subprocess.run(["intentgraph", ".", "--level", "medium"], 
                         capture_output=True, text=True)
data = json.loads(analysis.stdout)

# Analyze code structure for AI assistant
for file in data['files']:
    if file['complexity_score'] > 10:
        print(f"High complexity: {file['path']} (score: {file['complexity_score']})")
    
    key_symbols = [s['name'] for s in file['symbols'] 
                   if s['symbol_type'] == 'class']
    print(f"  Classes: {key_symbols}")
''',
        
        "full": '''
# Complete analysis for comprehensive AI tasks
analysis = subprocess.run(["intentgraph", ".", "--level", "full"], 
                         capture_output=True, text=True)
data = json.loads(analysis.stdout)

# Deep analysis for AI code generation
for file in data['files']:
    print(f"File: {file['path']}")
    print(f"  Purpose: {file.get('file_purpose', 'unknown')}")
    print(f"  Patterns: {file.get('design_patterns', [])}")
    
    for symbol in file['symbols']:
        if symbol.get('docstring'):
            print(f"  Function {symbol['name']}: {symbol['docstring'][:100]}...")
'''
    }
    
    for level, code in examples.items():
        print(f"\n  {level.upper()} Level Usage:")
        print(code)


if __name__ == "__main__":
    # Run the complete demo
    demo_output_levels()
    analyze_ai_suitability()
    demonstrate_content_differences()
    ai_token_limit_analysis()
    example_ai_agent_usage()
    
    print("\n🎉 Demo complete! IntentGraph's tiered output system ensures")
    print("   your AI agents can always access the right level of detail")
    print("   without hitting token limits.")