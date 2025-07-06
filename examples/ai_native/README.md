# AI-Native Interface Examples

This directory contains examples demonstrating IntentGraph's revolutionary **AI-native interface** that enables autonomous AI agents to analyze and understand codebases without human intervention.

## 🧠 **AI-Native Philosophy**

Traditional code analysis tools require:
- ❌ Human-crafted commands
- ❌ Manual output handling  
- ❌ Documentation reading
- ❌ Configuration setup

**IntentGraph's AI-native interface enables:**
- ✅ **Autonomous capability discovery** through self-describing manifests
- ✅ **Natural language queries** with intelligent semantic parsing
- ✅ **Task-aware response optimization** based on agent context
- ✅ **Token budget management** with adaptive detail levels
- ✅ **Intelligent navigation** without human guidance

## 🚀 **Quick Start for AI Agents**

### Basic Connection
```python
from intentgraph import connect_to_codebase

# AI agent connects autonomously
agent = connect_to_codebase("/path/to/repo", {
    "task": "bug_fixing",
    "token_budget": 30000,
    "agent_type": "code_reviewer"
})

# Natural language queries
results = agent.query("Find files with high complexity")
insights = agent.explore("security")
recommendations = agent.recommend_next_actions()
```

### Capability Discovery
```python
from intentgraph import get_capabilities_manifest

# AI agent discovers capabilities without human docs
capabilities = get_capabilities_manifest()

# Agent learns what it can do
analysis_types = capabilities["capabilities"]["analysis_types"]
query_interface = capabilities["capabilities"]["query_interface"] 
autonomous_features = capabilities["capabilities"]["autonomous_features"]
```

## 📚 **Examples**

### [`autonomous_agent_demo.py`](autonomous_agent_demo.py)
Comprehensive demonstration of AI-native capabilities:

- **Autonomous Discovery**: How agents discover capabilities
- **Natural Language Queries**: Semantic query interface
- **Task-Aware Optimization**: Response adaptation for different agent types
- **Autonomous Navigation**: Self-guided codebase exploration
- **Intelligent Clustering**: Large codebase navigation
- **Manifest-Driven Interaction**: Using self-describing capabilities

```bash
python autonomous_agent_demo.py /path/to/your/repository
```

## 🤖 **AI Agent Integration Patterns**

### Pattern 1: Autonomous Bug Finder
```python
# AI agent autonomously finds and analyzes bugs
agent = connect_to_codebase(repo_path, {
    "task": "bug_fixing",
    "token_budget": 30000
})

# Agent discovers high-risk areas
issues = agent.query("Find files with high complexity and recent changes")

# Agent analyzes specific problematic areas
for issue in issues["findings"]["files"]:
    if issue["complexity_score"] > 15:
        analysis = agent.get_focused_analysis([issue["path"]], "bug_analysis")
        
# Agent gets recommendations for next steps  
next_actions = agent.recommend_next_actions(analysis)
```

### Pattern 2: Feature Development Assistant
```python
# AI agent helps with feature development
agent = connect_to_codebase(repo_path, {
    "task": "feature_development",
    "token_budget": 50000
})

# Agent finds similar features for pattern learning
similar = agent.navigate_to_implementation("user authentication")

# Agent analyzes impact of proposed changes
impact = agent.analyze_impact(["src/auth/", "src/api/"])

# Agent explores extension points
extensions = agent.explore("authentication_extensions")

# Agent provides implementation guidance
guidance = extensions["navigation"]["next_actions"]
```

### Pattern 3: Security Audit Agent
```python
# AI agent performs autonomous security audit
agent = connect_to_codebase(repo_path, {
    "task": "security_audit",
    "token_budget": 40000,
    "expertise_level": "expert"
})

# Agent identifies security patterns
security_analysis = agent.query("Analyze authentication and authorization patterns")

# Agent finds potential vulnerabilities
vulnerabilities = agent.query("Find input validation and data sanitization issues")

# Agent provides security recommendations
recommendations = agent.recommend_next_actions(security_analysis)
```

## 🧩 **Intelligent Features**

### Self-Describing Capabilities
AI agents discover what they can do without reading human documentation:

```python
manifest = get_capabilities_manifest()

# Available analysis types
analysis_types = manifest["capabilities"]["analysis_types"]
# structural_analysis, semantic_analysis, quality_analysis, intelligent_clustering

# Query interface types  
query_types = manifest["capabilities"]["query_interface"]
# natural_language, semantic_queries, focused_analysis

# Autonomous features
autonomous = manifest["capabilities"]["autonomous_features"] 
# capability_discovery, intelligent_navigation, token_budget_management, context_awareness
```

### Task-Aware Response Optimization
Responses automatically adapt to agent context:

```python
# Bug fixing agent gets complexity-focused responses
bug_agent = connect_to_codebase(repo, {"task": "bug_fixing"})
bug_results = bug_agent.query("Analyze code quality")
# Response emphasizes: complexity_scores, error_patterns, recent_changes

# Feature development agent gets architecture-focused responses  
feature_agent = connect_to_codebase(repo, {"task": "feature_development"})
feature_results = feature_agent.query("Analyze code quality")
# Response emphasizes: extension_points, similar_patterns, interfaces
```

### Token Budget Management
Automatic response optimization for AI context limits:

```python
# Small budget - minimal responses
small_agent = connect_to_codebase(repo, {"token_budget": 5000})
small_results = small_agent.query("Explore codebase")
# Gets: focused_minimal_responses, single_concept_queries

# Large budget - comprehensive responses
large_agent = connect_to_codebase(repo, {"token_budget": 50000})  
large_results = large_agent.query("Explore codebase")
# Gets: comprehensive_responses, full_analysis_queries, clustering_enabled
```

### Intelligent Navigation
AI agents navigate codebases autonomously:

```python
agent = connect_to_codebase(repo_path, {"task": "code_understanding"})

# Agent explores autonomously
exploration = agent.explore()

# Agent gets intelligent recommendations  
recommendations = agent.recommend_next_actions(exploration)

# Agent follows recommendations automatically
for rec in recommendations:
    follow_up = agent.query(rec["query"])
    
# Agent manages token budget automatically
remaining = agent.get_token_budget_remaining()
if remaining < 10000:
    agent.set_token_budget(remaining)  # Auto-optimization
```

## 🎯 **Agent Task Optimization**

The AI interface automatically optimizes for different agent tasks:

| Agent Task | Response Focus | Optimal Clustering | Recommended Queries |
|------------|----------------|-------------------|-------------------|
| **bug_fixing** | Complexity, error patterns | analysis_mode | "Find high complexity files", "Analyze error handling" |
| **feature_development** | Extension points, interfaces | refactoring_mode | "Show extension points", "Find similar features" |
| **code_review** | Quality metrics, violations | analysis_mode | "Analyze quality metrics", "Find pattern violations" |
| **security_audit** | Security patterns, validation | feature_based | "Find input validation", "Analyze auth flows" |
| **refactoring** | Coupling, cohesion | refactoring_mode | "Analyze dependencies", "Find coupling issues" |
| **documentation** | Public APIs, architecture | navigation_mode | "Extract public APIs", "Show architecture" |

## 💡 **Best Practices for AI Agents**

### 1. Start with Capability Discovery
```python
# Always discover capabilities first
capabilities = get_capabilities_manifest()
task_patterns = capabilities["agent_interaction_patterns"]["task_based_optimization"]

# Select optimal strategy based on manifest
strategy = task_patterns[your_task]
```

### 2. Use Natural Language Queries
```python
# Natural language is preferred over structured queries
results = agent.query("Find security vulnerabilities in authentication")
# Better than manually constructing complex query objects
```

### 3. Follow Navigation Recommendations
```python
# Use autonomous navigation guidance
exploration = agent.explore()
next_actions = agent.recommend_next_actions(exploration)

# Follow AI recommendations for optimal exploration
for action in next_actions:
    agent.query(action["query"])
```

### 4. Monitor Token Budget
```python
# Check budget regularly for long-running analysis
remaining = agent.get_token_budget_remaining()
if remaining < 5000:
    # Switch to more focused queries
    agent.set_token_budget(remaining)
```

### 5. Use Task-Specific Optimization
```python
# Optimize agent for specific task
agent.optimize_for_task(AgentTask.BUG_FIXING)

# Or chain optimizations
agent.optimize_for_task(AgentTask.SECURITY_AUDIT).set_token_budget(20000)
```

## 🔗 **Integration Examples**

### With LangChain Agents
```python
from langchain.agents import Tool
from intentgraph import connect_to_codebase

def create_codebase_tool(repo_path: str):
    agent = connect_to_codebase(repo_path)
    
    return Tool(
        name="codebase_analyzer",
        description="Analyze codebase structure and quality",
        func=lambda query: agent.query(query)
    )
```

### With AutoGen Agents  
```python
import autogen
from intentgraph import connect_to_codebase

class CodebaseAnalysisAgent(autogen.AssistantAgent):
    def __init__(self, repo_path: str, **kwargs):
        super().__init__(**kwargs)
        self.codebase_agent = connect_to_codebase(repo_path, {
            "agent_type": "autogen_assistant"
        })
    
    def analyze_codebase(self, query: str):
        return self.codebase_agent.query(query)
```

### With Custom AI Frameworks
```python
class MyAIAgent:
    def __init__(self, repo_path: str):
        self.codebase = connect_to_codebase(repo_path, {
            "task": "feature_development",
            "agent_type": "custom_ai_agent"
        })
    
    def understand_codebase(self):
        # Autonomous exploration
        exploration = self.codebase.explore()
        
        # Get AI recommendations  
        recommendations = self.codebase.recommend_next_actions(exploration)
        
        # Follow autonomous guidance
        for rec in recommendations:
            analysis = self.codebase.query(rec["query"])
            
        return analysis
```

## 🚀 **Getting Started**

1. **Install IntentGraph** with AI interface:
   ```bash
   pip install intentgraph>=0.3.0
   ```

2. **Run the demo** to see AI-native capabilities:
   ```bash
   python autonomous_agent_demo.py /path/to/your/repo
   ```

3. **Integrate with your AI agent**:
   ```python
   from intentgraph import connect_to_codebase
   
   agent = connect_to_codebase("/path/to/repo", {
       "task": "your_task",
       "token_budget": 30000
   })
   
   results = agent.query("Your natural language query")
   ```

## 🔮 **The Future of AI-Codebase Interaction**

IntentGraph's AI-native interface represents the evolution from **AI-friendly** to **AI-usable** tools:

- **No more manual commands** - AI agents use natural language
- **No more human documentation** - Self-describing capabilities  
- **No more configuration** - Automatic optimization for agent context
- **No more token waste** - Intelligent budget management
- **No more blind navigation** - Autonomous exploration with guidance

This is the foundational layer for **true autonomous coding agents** that can understand, navigate, and act upon codebases without human mediation! 🤖✨