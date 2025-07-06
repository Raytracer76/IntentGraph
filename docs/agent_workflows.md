# AI Agent Workflows

This guide demonstrates how AI agents can leverage IntentGraph's **AI-native interface** for autonomous coding tasks without human intervention.

## 🆕 **AI-Native Interface Overview**

IntentGraph v0.3.0+ introduces a revolutionary AI-native interface that transforms how AI agents interact with codebases:

- **🧠 Autonomous Capability Discovery** - Agents discover what they can do without human docs
- **🗣️ Natural Language Queries** - No more manual command construction
- **🎯 Task-Aware Optimization** - Responses adapt to agent context
- **💰 Token Budget Management** - Automatic optimization for AI context limits
- **🧭 Intelligent Navigation** - Self-guided exploration with recommendations
- **📋 Self-Describing Interface** - Manifest-driven interaction patterns

## 🚀 **Getting Started: AI-Native Workflows**

### 1. Autonomous Agent Connection
```python
from intentgraph import connect_to_codebase

# AI agent connects with context
agent = connect_to_codebase("/path/to/repo", {
    "task": "bug_fixing",           # or "feature_development", "security_audit", etc.
    "token_budget": 30000,          # AI agent's available token budget
    "agent_type": "code_reviewer",  # Agent identification
    "expertise_level": "expert"     # Agent's expertise level
})
```

### 2. Autonomous Capability Discovery
```python
from intentgraph import get_capabilities_manifest

# AI agent discovers capabilities without human documentation
capabilities = get_capabilities_manifest()

# Agent learns available analysis types
analysis_types = capabilities["capabilities"]["analysis_types"]
# structural_analysis, semantic_analysis, quality_analysis, intelligent_clustering

# Agent discovers query interface types
query_types = capabilities["capabilities"]["query_interface"]
# natural_language, semantic_queries, focused_analysis

# Agent finds autonomous features
autonomous_features = capabilities["capabilities"]["autonomous_features"]
# capability_discovery, intelligent_navigation, token_budget_management
```

### 3. Natural Language Queries
```python
# AI agents use natural language instead of commands
results = agent.query("Find files with high complexity that might contain bugs")
insights = agent.query("Show me the authentication and security patterns")
analysis = agent.query("Analyze the database access patterns for potential issues")

# Each query automatically:
# - Parses natural language intent
# - Optimizes for agent's task context
# - Manages token budget efficiently
# - Provides navigation guidance
```

## 🎯 **Task-Specific AI Agent Patterns**

### Bug Fixing Agent
```python
# AI agent optimized for bug detection and analysis
bug_agent = connect_to_codebase("/path/to/repo", {
    "task": "bug_fixing",
    "token_budget": 20000,
    "expertise_level": "expert"
})

# Agent autonomously finds problematic areas
issues = bug_agent.query("Find potential problem areas")

# Agent analyzes specific high-risk files
for file_path in issues["high_priority_files"]:
    analysis = bug_agent.query(f"Analyze {file_path} for bug patterns")
    
# Agent gets next action recommendations
recommendations = bug_agent.recommend_next_actions(issues)
```

### Feature Development Agent
```python
# AI agent optimized for feature development
feature_agent = connect_to_codebase("/path/to/repo", {
    "task": "feature_development", 
    "token_budget": 50000,
    "expertise_level": "intermediate"
})

# Agent finds extension points
extensions = feature_agent.query("Show extension points for new features")

# Agent analyzes similar existing features
similar = feature_agent.query("Find similar authentication features")

# Agent explores architecture patterns
patterns = feature_agent.explore("authentication_patterns")
```

### Security Audit Agent
```python
# AI agent optimized for security analysis
security_agent = connect_to_codebase("/path/to/repo", {
    "task": "security_audit",
    "token_budget": 40000,
    "expertise_level": "expert"
})

# Agent identifies security patterns
security_analysis = security_agent.query("Analyze authentication and authorization patterns")

# Agent finds potential vulnerabilities  
vulnerabilities = security_agent.query("Find input validation and data sanitization issues")

# Agent provides security recommendations
recommendations = security_agent.recommend_next_actions(security_analysis)
```

## 🧭 **Autonomous Navigation Patterns**

### Self-Guided Exploration
```python
# AI agent starts autonomous exploration
agent = connect_to_codebase("/path/to/repo", {
    "task": "code_understanding",
    "token_budget": 50000
})

# Step 1: Agent explores autonomously
exploration = agent.explore()

# Step 2: Agent gets intelligent recommendations
recommendations = agent.recommend_next_actions(exploration)

# Step 3: Agent follows recommendations autonomously
for rec in recommendations:
    follow_up = agent.query(rec["query"])
    
# Step 4: Agent manages token budget automatically
remaining = agent.get_token_budget_remaining()
if remaining < 10000:
    agent.set_token_budget(remaining)  # Auto-optimization
```

### Focused Area Investigation
```python
# AI agent investigates specific area
agent = connect_to_codebase("/path/to/repo", {"task": "security_audit"})

# Agent explores specific focus area
security_exploration = agent.explore("security")

# Agent gets security-specific navigation
security_nav = agent.navigate_to_implementation("authentication")

# Agent follows security-focused recommendations
if security_nav["strategy"] == "cluster_navigation":
    relevant_clusters = security_nav["relevant_clusters"]
    for cluster in relevant_clusters:
        cluster_analysis = agent.query(f"Analyze security patterns in {cluster}")
```

## 💰 **Token Budget Management**

### Automatic Budget Optimization
```python
# AI agents automatically optimize for their token budget

# Small budget agent - gets minimal, focused responses
small_agent = connect_to_codebase("/path/to/repo", {"token_budget": 5000})
small_results = small_agent.query("Explore codebase")
# Response: focused_minimal_responses, single_concept_queries

# Large budget agent - gets comprehensive responses  
large_agent = connect_to_codebase("/path/to/repo", {"token_budget": 50000})
large_results = large_agent.query("Explore codebase") 
# Response: comprehensive_responses, full_analysis_queries, clustering_enabled
```

### Dynamic Budget Adjustment
```python
# AI agent dynamically adjusts based on remaining budget
agent = connect_to_codebase("/path/to/repo", {"token_budget": 30000})

exploration = agent.explore()  # Uses ~8000 tokens

# Check remaining budget
remaining = agent.get_token_budget_remaining()  # ~22000 tokens

if remaining < 15000:
    # Agent automatically switches to more focused queries
    agent.set_response_optimization("focused")
    
# Continue with optimized budget
focused_analysis = agent.query("Find the most critical issues")
```

## 🧩 **Intelligent Clustering Navigation**

### Large Codebase Navigation
```python
# AI agent automatically uses clustering for large repositories
agent = connect_to_codebase("/path/to/large-repo", {
    "task": "feature_development",
    "token_budget": 30000
})

# Agent automatically detects need for clustering
cluster_results = agent.navigate_to_implementation("authentication")

if cluster_results["strategy"] == "cluster_navigation":
    # Agent gets cluster overview
    cluster_overview = cluster_results["cluster_overview"]
    
    # Agent gets AI recommendations for clusters
    recommendations = cluster_overview["cluster_recommendations"]
    
    # Agent explores recommended clusters
    for cluster_type, clusters in recommendations.items():
        if cluster_type == "authentication_related":
            for cluster in clusters:
                analysis = agent.query(f"Analyze authentication patterns in {cluster}")
```

### Cluster-Aware Query Optimization
```python
# AI agent optimizes queries based on clustering strategy
agent = connect_to_codebase("/path/to/repo", {"task": "refactoring"})

# Agent gets cluster recommendations for refactoring
capabilities = get_capabilities_manifest()
task_patterns = capabilities["agent_interaction_patterns"]["task_based_optimization"]
refactoring_pattern = task_patterns["refactoring"]

# Agent uses recommended clustering mode
optimal_clustering = refactoring_pattern["optimal_clustering"]  # "refactoring_mode"

# Agent follows task-specific query recommendations
recommended_queries = refactoring_pattern["recommended_queries"]
for query in recommended_queries:
    results = agent.query(query)
```

## 🔄 **Manifest-Driven Workflows**

### Autonomous Workflow Selection
```python
# AI agent uses manifest to select optimal workflow
capabilities = get_capabilities_manifest()

# Agent reads available interaction patterns
interaction_patterns = capabilities["agent_interaction_patterns"]
task_patterns = interaction_patterns["task_based_optimization"]

# Agent selects pattern based on its task
agent_task = "bug_fixing"
if agent_task in task_patterns:
    pattern = task_patterns[agent_task]
    
    # Agent follows manifest guidance
    recommended_queries = pattern["recommended_queries"]
    optimal_clustering = pattern["optimal_clustering"]
    response_focus = pattern["response_focus"]
    
    # Agent executes based on manifest
    agent = connect_to_codebase("/path/to/repo", {"task": agent_task})
    
    # Agent uses recommended queries
    for query in recommended_queries:
        results = agent.query(query)
```

### Usage Example Discovery
```python
# AI agent discovers usage patterns from manifest
capabilities = get_capabilities_manifest()
usage_examples = capabilities["usage_examples"]

# Agent learns available workflow patterns
for workflow_name, workflow_details in usage_examples.items():
    print(f"Workflow: {workflow_name}")
    print(f"Description: {workflow_details['description']}")
    
    # Agent can execute the workflow
    if workflow_name == "autonomous_bug_fixing":
        exec(workflow_details["code_example"])
```

## 🚀 **Advanced AI Agent Patterns**

### Multi-Agent Collaboration
```python
# Multiple AI agents with different specializations
bug_agent = connect_to_codebase("/path/to/repo", {"task": "bug_fixing"})
security_agent = connect_to_codebase("/path/to/repo", {"task": "security_audit"})
feature_agent = connect_to_codebase("/path/to/repo", {"task": "feature_development"})

# Agents share findings
bug_results = bug_agent.query("Find high complexity areas")
security_results = security_agent.query("Find security vulnerabilities")

# Feature agent considers both perspectives
feature_context = {
    "bug_findings": bug_results,
    "security_findings": security_results
}
feature_plan = feature_agent.query("Plan new feature considering existing issues")
```

### Adaptive Learning Agents
```python
# AI agent adapts based on repository characteristics
agent = connect_to_codebase("/path/to/repo", {"task": "code_understanding"})

# Agent starts with exploration
initial_exploration = agent.explore()

# Agent adapts strategy based on findings
repo_characteristics = initial_exploration.get("repository_characteristics", {})

if repo_characteristics.get("complexity") == "high":
    # Agent switches to focused analysis mode
    agent.set_response_optimization("detailed")
elif repo_characteristics.get("size") == "large":
    # Agent enables clustering
    agent.enable_clustering("analysis_mode")
    
# Agent continues with adapted strategy
adapted_analysis = agent.query("Provide detailed architecture analysis")
```

## 🔧 **Integration Patterns**

### LangChain Integration
```python
from langchain.agents import Tool
from intentgraph import connect_to_codebase

def create_intentgraph_tool(repo_path: str):
    agent = connect_to_codebase(repo_path)
    
    return Tool(
        name="codebase_analyzer",
        description="Analyze codebase structure and quality using natural language",
        func=lambda query: agent.query(query)
    )

# Use in LangChain agent
codebase_tool = create_intentgraph_tool("/path/to/repo")
```

### AutoGen Integration
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

### Custom AI Framework Integration
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

## 🎯 **Best Practices for AI Agents**

### 1. Always Start with Capability Discovery
```python
# Discover capabilities before any interaction
capabilities = get_capabilities_manifest()
task_patterns = capabilities["agent_interaction_patterns"]["task_based_optimization"]

# Select optimal strategy based on manifest
strategy = task_patterns[your_task]
```

### 2. Use Natural Language Queries
```python
# Prefer natural language over structured queries
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

## 🔮 **The Future of AI-Codebase Interaction**

IntentGraph's AI-native interface represents the evolution from **AI-friendly** to **AI-usable** tools:

- **No more manual commands** - AI agents use natural language
- **No more human documentation** - Self-describing capabilities
- **No more configuration** - Automatic optimization for agent context
- **No more token waste** - Intelligent budget management
- **No more blind navigation** - Autonomous exploration with guidance

This is the foundational layer for **true autonomous coding agents** that can understand, navigate, and act upon codebases without human mediation! 🤖✨

---

**Ready to build autonomous AI agents?** Check out the [complete examples](../examples/ai_native/README.md) to see the AI-native interface in action.