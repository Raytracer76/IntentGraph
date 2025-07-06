# IntentGraph 🧠

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**AI-Ready Codebase Intelligence** - Transform any codebase into rich, queryable intelligence optimized for AI token limits and agent workflows.

## 🎯 **Why IntentGraph?**

AI coding agents are everywhere, but they're **flying blind** through codebases:
- ❌ Constantly scanning files to understand structure
- ❌ Missing function-level relationships
- ❌ No semantic understanding of code purpose
- ❌ Reinventing analysis on every interaction

**IntentGraph solves this** by providing comprehensive codebase intelligence upfront.

## ✨ **What Makes It Special**

### **🔍 Deep Code Analysis**
```json
{
  "symbols": [
    {
      "name": "LanguageParser", 
      "symbol_type": "class",
      "signature": "class LanguageParser(ABC)",
      "docstring": "Abstract base class for language-specific parsers.",
      "is_exported": true,
      "line_start": 10,
      "line_end": 45
    }
  ],
  "function_dependencies": [
    {
      "from_symbol": "analyze",
      "to_symbol": "build_graph", 
      "dependency_type": "calls",
      "line_number": 127
    }
  ],
  "file_purpose": "parsing",
  "design_patterns": ["adapter", "parser"],
  "complexity_score": 4,
  "maintainability_index": 82.5
}
```

### **🧠 AI Agent Intelligence**
- **Function-level dependency tracking** - Know exactly what calls what
- **API surface mapping** - Clear public interfaces vs internal implementation  
- **Semantic analysis** - File purposes, design patterns, key abstractions
- **Code quality metrics** - Complexity scores, maintainability indices
- **Rich metadata** - Signatures, docstrings, decorators, line numbers

### **⚡ Developer Productivity**
- **Smart refactoring** - Understand impact before changing code
- **Architecture compliance** - Detect and enforce design patterns
- **Code review automation** - Flag complex/unmaintainable code
- **Onboarding acceleration** - Quickly understand large codebases

## 🚀 **Quick Start**

### **Installation**
```bash
pip install intentgraph
```

### **Basic Usage**
```bash
# Analyze current directory (AI-friendly minimal output ~10KB)
intentgraph .

# Generate detailed report
intentgraph . --output analysis.json

# Focus on specific languages
intentgraph . --lang py,js,ts
```

### **🤖 AI-Optimized Output Levels**
IntentGraph offers three output levels optimized for different use cases:

```bash
# Minimal: ~10KB, perfect for AI agents (DEFAULT)
intentgraph . --level minimal

# Medium: ~70KB, balanced analysis for complex AI tasks  
intentgraph . --level medium

# Full: ~340KB, comprehensive analysis for audits
intentgraph . --level full
```

| Level | Size | Best For | Contains |
|-------|------|----------|----------|
| **minimal** | ~10KB | AI agents, quick analysis | Paths, dependencies, imports, basic metrics |
| **medium** | ~70KB | Detailed AI tasks, code review | + Key symbols, exports, maintainability scores |
| **full** | ~340KB | Comprehensive audits | Complete analysis with all metadata |

**Why this matters:** AI agents have token limits (~200KB). Minimal output ensures your entire codebase intelligence fits in any AI context window.

### **🧩 Intelligent Clustering for Large Codebases**
For massive repositories that exceed AI token limits even with minimal output, IntentGraph offers intelligent clustering:

```bash
# Break large codebase into manageable clusters
intentgraph . --cluster --cluster-mode analysis --cluster-size 15KB

# Different clustering strategies for different use cases
intentgraph . --cluster --cluster-mode refactoring --cluster-size 10KB
intentgraph . --cluster --cluster-mode navigation --cluster-size 20KB
```

**Cluster Modes:**
- **`analysis`** - Dependency-based clustering for code understanding
- **`refactoring`** - Feature-based clustering for making targeted changes  
- **`navigation`** - Size-optimized clustering for large codebase exploration

**Output Structure:**
```
output/
├── index.json          # Master navigation index
├── domain.json         # Core domain models cluster
├── application.json    # Application services cluster
├── adapters.json       # External interfaces cluster
└── utilities.json      # Helper functions cluster
```

**Smart Index for AI Navigation:**
```json
{
  "clusters": [
    {
      "cluster_id": "domain",
      "name": "Domain Layer", 
      "description": "Core business logic and models",
      "file_count": 5,
      "total_size_kb": 12.4,
      "primary_concerns": ["data_models", "business_rules"],
      "complexity_score": 15
    }
  ],
  "cluster_recommendations": {
    "understanding_codebase": ["domain", "application"],
    "making_changes": ["adapters", "application"],
    "finding_bugs": ["utilities", "domain"],
    "adding_features": ["application", "adapters"]
  }
}
```

**Revolutionary for AI Agents:** Instead of cramming everything into context, AI agents intelligently navigate clusters based on their specific task!

### **Sample Output**
```bash
[2025-01-15 10:30:14] INFO     Found 42 source files                              
[2025-01-15 10:30:18] INFO     Analysis complete!                                  

     Analysis Summary     
┏━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric         ┃ Value ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Files analyzed │ 42    │
│ Functions      │ 156   │
│ Classes        │ 28    │
│ Dependencies   │ 89    │
│ Avg Complexity │ 3.2   │
└────────────────┴───────┘
```

## 🎯 **Perfect For**

### **🤖 AI Coding Agents**
```python
# Instead of scanning files repeatedly
agent.scan_codebase()  # Slow, incomplete

# Use IntentGraph intelligence
analysis = load_intentgraph_report("analysis.json")
agent.understand_codebase(analysis)  # Fast, comprehensive
```

### **🔧 Developer Tools**
- **IDE Extensions** - Smart navigation and completion
- **Code Review Tools** - Automated quality assessment  
- **Documentation Generators** - Extract API surfaces
- **Refactoring Tools** - Safe transformation guidance

### **📊 Engineering Management**
- **Technical Debt Assessment** - Quantify code quality
- **Architecture Compliance** - Monitor design patterns
- **Developer Onboarding** - Codebase understanding maps
- **Legacy Modernization** - Identify improvement opportunities

## 📖 **Comprehensive Example**

### **Input: Your Codebase**
```
my-project/
├── src/
│   ├── models.py      # Data structures
│   ├── parser.py      # Text processing  
│   └── api.py         # Web interface
└── tests/
    └── test_models.py
```

### **Output: Rich Intelligence**
```json
{
  "files": [
    {
      "path": "src/models.py",
      "symbols": [
        {
          "name": "User",
          "symbol_type": "class", 
          "signature": "class User(BaseModel)",
          "exports": ["User"],
          "complexity_score": 2
        }
      ],
      "file_purpose": "data_models",
      "key_abstractions": ["User", "Profile"],
      "design_patterns": ["model"]
    },
    {
      "path": "src/api.py",
      "function_dependencies": [
        {
          "from_symbol": "create_user",
          "to_symbol": "User.__init__",
          "dependency_type": "instantiates",
          "line_number": 45
        }
      ],
      "file_purpose": "web_interface", 
      "complexity_score": 8
    }
  ]
}
```

### **What AI Agents Get**
- **"To modify User model, check impact on api.py:45 create_user function"**
- **"This file follows the Model pattern with 2 complexity score"**
- **"Public API exports: User, Profile classes"**
- **"Dependencies: User model is instantiated in API layer"**

## 🏗️ **Architecture**

IntentGraph follows **Clean Architecture** principles:

```
┌─────────────────┐
│   CLI Layer     │  ← Command-line interface
├─────────────────┤
│ Application     │  ← Analysis orchestration  
├─────────────────┤
│   Domain        │  ← Core models & logic
├─────────────────┤
│ Infrastructure  │  ← Parsers & adapters
└─────────────────┘
```

### **Key Components**
- **Enhanced Parsers** - Deep AST analysis for each language
- **Semantic Analyzer** - Pattern detection and purpose inference
- **Dependency Tracker** - Function-level relationship mapping
- **Quality Calculator** - Complexity and maintainability metrics

## 🌐 **Language Support**

| Language   | Status | Features |
|------------|--------|----------|
| **Python** | ✅ Full | Functions, classes, decorators, complexity |
| JavaScript | 🚧 Basic | File dependencies only |
| TypeScript | 🚧 Basic | File dependencies only |
| Go | 🚧 Basic | File dependencies only |

**Coming Soon:** Enhanced analysis for JavaScript, TypeScript, Go, Rust, Java

## ⚙️ **Configuration**

### **Command Line Options**
```bash
intentgraph [OPTIONS] REPOSITORY_PATH

Analysis Options:
  -o, --output FILE           Output file (- for stdout) [default: stdout]
  --level [minimal|medium|full] Analysis detail level [default: minimal]
                             minimal (~10KB, AI-friendly)
                             medium (~70KB, balanced) 
                             full (~340KB, complete)
  --lang TEXT                 Languages to analyze [default: auto-detect]
  --include-tests            Include test files in analysis
  --format [pretty|compact]  JSON output format [default: pretty]
  --show-cycles              Print dependency cycles and exit with code 2
  --workers INTEGER          Parallel workers [default: CPU count]
  --debug                    Enable debug logging

Clustering Options:
  --cluster                  Enable cluster mode for large codebase navigation
  --cluster-mode [analysis|refactoring|navigation]
                             Clustering strategy [default: analysis]
                             analysis: dependency-based grouping
                             refactoring: feature-based grouping
                             navigation: size-optimized grouping
  --cluster-size [10KB|15KB|20KB]
                             Target cluster size [default: 15KB]
  --index-level [basic|rich] Index detail level [default: rich]
                             basic: simple file mapping
                             rich: full metadata with AI recommendations
```

### **Programmatic Usage**
```python
from intentgraph import RepositoryAnalyzer

analyzer = RepositoryAnalyzer(
    language_filter=['python'],
    include_tests=False,
    workers=4
)

result = analyzer.analyze('/path/to/repo')
print(f"Found {len(result.files)} files")
print(f"Total complexity: {sum(f.complexity_score for f in result.files)}")
```

## 🔧 **Development**

### **Setup**
```bash
git clone https://github.com/Raytracer76/intentgraph.git
cd intentgraph
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
pip install -e ".[dev]"
```

### **Testing**
```bash
pytest --cov=intentgraph --cov-report=term-missing
```

### **Code Quality**
```bash
ruff format .           # Format code
ruff check --fix .      # Lint and auto-fix
mypy .                  # Type checking
```

## 🤝 **Contributing**

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### **Adding Language Support**
1. Create parser in `src/intentgraph/adapters/parsers/`
2. Implement `extract_code_structure()` method
3. Add tests and examples
4. Submit PR with documentation

### **Ideas for Contributions**
- **Enhanced JavaScript/TypeScript parser** 
- **Go/Rust language support**
- **Visual dependency graph generator**
- **VS Code extension**
- **Performance optimizations**
- **ML-based pattern detection**

## 📊 **Benchmarks**

| Repository Size | Files | Analysis Time | Output Size |
|----------------|-------|---------------|-------------|
| Small (< 50 files) | 42 | 2.3s | 180KB |
| Medium (< 500 files) | 287 | 12.1s | 2.1MB |
| Large (< 2000 files) | 1,654 | 45.7s | 18.3MB |

*Benchmarks on MacBook Pro M2, Python 3.12*

## 🎯 **Use Cases**

### **For AI Agents**
```python
# Perfect for AI agents - default minimal output fits any token limit
analysis = intentgraph.analyze(repo_path)  # ~10KB output

# For detailed AI analysis tasks  
analysis = intentgraph.analyze(repo_path, level="medium")  # ~70KB output

# For massive codebases - intelligent clustering
cluster_result = intentgraph.cluster(repo_path, mode="analysis")

# AI reads index.json first to understand structure
with open("analysis/index.json") as f:
    index = json.load(f)

# Then loads specific clusters based on task
target_clusters = index["cluster_recommendations"]["making_changes"]
for cluster_id in target_clusters:
    with open(f"analysis/{cluster_id}.json") as f:
        cluster_data = json.load(f)
    # Process cluster_data...

# Now AI knows:
# - Which functions call which (no file scanning)
# - Public APIs vs internal implementation  
# - Code complexity and quality metrics
# - Architectural patterns and purposes
# - Smart navigation strategy for large codebases
```

### **For Developer Tools**
```python
# Code review automation
high_complexity = [f for f in analysis.files if f.complexity_score > 10]

# Architecture compliance  
missing_patterns = find_files_without_patterns(analysis, required=['adapter'])

# Refactoring safety
impact = find_function_dependencies(analysis, target_function="process_data")
```

### **For Documentation**
```python
# Auto-generate API docs
public_apis = [e for f in analysis.files for e in f.exports if not e.name.startswith('_')]

# Architecture diagrams
dependency_graph = build_graph(analysis.function_dependencies)
```

## 🏆 **Why Choose IntentGraph**

| Feature | IntentGraph | GitHub Dependency Graph | SonarQube | Tree-sitter |
|---------|-------------|-------------------------|-----------|-------------|
| **Function-level deps** | ✅ | ❌ | ❌ | ❌ |
| **Semantic analysis** | ✅ | ❌ | ❌ | ❌ |
| **AI-optimized output** | ✅ (3 levels) | ❌ | ❌ | ❌ |
| **Token limit friendly** | ✅ (~10KB) | ❌ | ❌ | ❌ |
| **Intelligent clustering** | ✅ (3 modes) | ❌ | ❌ | ❌ |
| **AI navigation index** | ✅ | ❌ | ❌ | ❌ |
| **Multi-language unified** | ✅ | ✅ | ✅ | ❌ |
| **Quality metrics** | ✅ | ❌ | ✅ | ❌ |
| **Design patterns** | ✅ | ❌ | ❌ | ❌ |

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- Built with [Typer](https://typer.tiangolo.com/) for CLI
- Uses [grimp](https://github.com/seddonym/grimp) for Python dependency analysis  
- Powered by Python's [ast](https://docs.python.org/3/library/ast.html) module for code parsing
- Graph operations via [NetworkX](https://networkx.org/)

## 📞 **Support**

- **GitHub Issues** - Bug reports and feature requests
- **Discussions** - Questions and community chat
- **Documentation** - Comprehensive guides and examples

---

**Made with ❤️ for the AI coding agent era**

*Transform your codebase into intelligence. Your future AI assistant will thank you.* 🤖✨