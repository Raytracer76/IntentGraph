# IntentGraph 🧬

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Your Codebase's Genome** - Pre-digested, structured, AI-optimized intelligence that unlocks true autonomous coding agents.

## 🧠 **Built for the GPT-4+ Era**

LLMs like GPT-4o and Claude 3.5 are powerful—but **limited by context**. They can understand structure, but not without intelligent input.

**The Problem**: Tool builders are struggling to make codebases context-fit into limited tokens (~200KB).

**The Solution**: IntentGraph feeds them pre-digested codebase intelligence to enable true autonomous coding.

## 🎯 **Who This Is For**

### 🏗️ **Primary: Platform Builders** 
Building the next generation of AI coding tools? IntentGraph is your foundational intelligence layer:
- **IDE Extensions** (VS Code, Cursor, etc.) - Smart navigation and completion
- **AI Coding Agents** (GitHub Copilot, CodeT5, etc.) - Context-aware code understanding
- **Developer Platforms** - Embedded codebase intelligence APIs

### 🤖 **Secondary: AI Tool Builders**
Creating specialized coding agents or analysis tools:
- **Code Review Automation** - Quality assessment and pattern detection
- **Refactoring Tools** - Safe transformation guidance with dependency awareness
- **Documentation Generators** - API surface extraction and architectural mapping

### 👨‍💻 **Tertiary: Individual Developers**
Direct usage for productivity and codebase understanding:
- **Large Codebase Navigation** - Intelligent clustering for massive repos
- **Technical Debt Assessment** - Quantified code quality metrics
- **Onboarding Acceleration** - Rapid understanding of unfamiliar codebases

## ⚡ **The Challenge IntentGraph Solves**

Traditional approaches fail with modern codebases:
- ❌ **File scanning**: Constantly re-analyzing to understand structure
- ❌ **Missing relationships**: No function-level dependency tracking
- ❌ **Token explosion**: Large codebases exceed AI context limits
- ❌ **No semantics**: Tools can't understand code purpose or patterns

**IntentGraph provides comprehensive intelligence upfront** - your codebase's structured genome.

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

# Generate cluster analysis (outputs to .intentgraph/ by default)
intentgraph . --cluster

# Generate detailed report
intentgraph . --output analysis.json

# Focus on specific languages
intentgraph . --lang py,js,ts
```

💡 **Pro tip**: Add `.intentgraph/` to your `.gitignore` - it's generated output like `.pytest_cache/`

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
```

**Visual Flow:**
```
🏢 Large Codebase (2MB+) ─┬─🧩 Clustering ─┬─📁 domain.json (15KB)
                          │                 ├─📁 adapters.json (12KB) 
                          │                 ├─📁 utilities.json (14KB)
                          └─📋 index.json ──┴─📁 application.json (13KB)
                             (AI Navigation Map)
```

**Real AI Agent Workflow:**
```
🤖 "I need to fix a bug in the billing logic"

1️⃣ AI reads index.json first:
   "cluster_recommendations": {
     "finding_bugs": ["domain", "utilities"]
   }

2️⃣ AI loads domain.json:
   Contains: billing_service.py, payment_models.py
   
3️⃣ AI identifies issue and fixes bug
   Without ever loading the entire 2MB codebase!
```

**Three Clustering Strategies:**

| Mode | Strategy | Best For | Example Use Case |
|------|----------|----------|------------------|
| **`analysis`** | Dependency-based | Code understanding | 🧠 "Help me understand this codebase" |
| **`refactoring`** | Feature-based | Targeted changes | ⚡ "Refactor the authentication system" |  
| **`navigation`** | Size-optimized | Large repo exploration | 🗺️ "Find all API endpoints in this 10MB repo" |

**Cluster Output Structure:**
```
.intentgraph/              # Default output (gitignore-friendly)
├── index.json            # 🧭 AI Navigation Map
│   ├── cluster_recommendations: {"finding_bugs": ["domain"]}
│   ├── cross_cluster_dependencies: [...]
│   └── file_to_cluster_map: {...}
├── domain.json           # 🏗️ Core business logic
├── adapters.json         # 🔌 External interfaces  
├── application.json      # ⚙️ Application services
└── utilities.json        # 🛠️ Helper functions
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

📚 **[Complete Language Support Guide →](docs/language_support.md)**

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

### **🏗️ Platform Builders**
Embed IntentGraph into your AI coding platform:
- **IDE Extensions** - Smart navigation, completion, refactoring assistance
- **AI Coding Agents** - Context-aware code understanding and generation  
- **Developer Platforms** - Codebase intelligence APIs for your tools

### **🤖 AI Tool Builders** 
Build specialized coding agents and analysis tools:
- **Code Review Automation** - Quality assessment and pattern detection
- **Refactoring Assistants** - Safe transformation with dependency awareness
- **Documentation Generators** - API extraction and architectural mapping

### **👨‍💻 Individual Developers**
Direct productivity and understanding:
- **Large Codebase Navigation** - Intelligent clustering for massive repos
- **Technical Debt Assessment** - Quantified quality metrics and improvement guidance
- **Team Onboarding** - Rapid understanding of unfamiliar codebases

🤖 **[Complete AI Agent Workflow Guide →](docs/agent_workflows.md)**

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