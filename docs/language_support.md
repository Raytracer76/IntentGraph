# Language Support

IntentGraph provides varying levels of analysis across different programming languages, with Python offering the most comprehensive support.

## Current Support Matrix

| Language | Status | File Dependencies | Symbol Analysis | Complexity Metrics | Design Patterns |
|----------|--------|-------------------|-----------------|-------------------|-----------------|
| **Python** | ✅ Full | ✅ | ✅ | ✅ | ✅ |
| **JavaScript** | 🚧 Basic | ✅ | ❌ | ❌ | ❌ |
| **TypeScript** | 🚧 Basic | ✅ | ❌ | ❌ | ❌ |
| **Go** | 🚧 Basic | ✅ | ❌ | ❌ | ❌ |

## Python Support (Full)

Python receives comprehensive analysis through enhanced AST parsing:

### Features
- **Deep Symbol Analysis**: Classes, functions, methods, variables
- **Function-level Dependencies**: Calls, instantiations, inheritance
- **Quality Metrics**: Complexity scores, maintainability indices
- **Design Pattern Detection**: Factory, adapter, singleton, etc.
- **API Surface Mapping**: Public/private distinction, exports
- **Rich Metadata**: Docstrings, decorators, type hints

### Example Output
```json
{
  "path": "src/models.py",
  "language": "python",
  "symbols": [
    {
      "name": "UserModel",
      "symbol_type": "class",
      "signature": "class UserModel(BaseModel)",
      "docstring": "User data model with validation",
      "decorators": ["@dataclass"],
      "line_start": 15,
      "line_end": 45,
      "is_exported": true
    }
  ],
  "function_dependencies": [
    {
      "from_symbol": "create_user",
      "to_symbol": "UserModel.__init__",
      "dependency_type": "instantiates",
      "line_number": 67
    }
  ],
  "complexity_score": 4,
  "maintainability_index": 82.5,
  "design_patterns": ["model", "factory"]
}
```

### Python-Specific Analysis
- **Import Resolution**: Tracks both relative and absolute imports
- **Decorator Analysis**: Understands framework decorators (Flask, Django, etc.)
- **Type Hint Processing**: Extracts type information for better understanding
- **Magic Method Detection**: Identifies special methods and their purposes
- **Property Analysis**: Distinguishes properties from regular methods

## JavaScript Support (Basic)

Currently provides file-level dependency analysis only:

### Features
- **Import/Export Tracking**: ES6 modules, CommonJS requires
- **File Dependencies**: Module relationship mapping
- **Basic Structure**: File organization and module boundaries

### Limitations
- No function-level dependency tracking
- No complexity metrics
- No symbol analysis
- No design pattern detection

### Example Output
```json
{
  "path": "src/utils.js",
  "language": "javascript", 
  "dependencies": ["./models", "lodash", "axios"],
  "imports": [
    "import { UserModel } from './models'",
    "import _ from 'lodash'",
    "import axios from 'axios'"
  ],
  "loc": 156
}
```

## TypeScript Support (Basic)

Similar to JavaScript with additional type information awareness:

### Features
- **Type Import Tracking**: Distinguishes type-only imports
- **Interface Dependencies**: Basic interface relationship detection
- **Module System**: Full ES6 and CommonJS support

### Example Output
```json
{
  "path": "src/types.ts",
  "language": "typescript",
  "dependencies": ["./interfaces", "express"],
  "imports": [
    "import type { User } from './interfaces'",
    "import { Request, Response } from 'express'"
  ],
  "loc": 89
}
```

## Go Support (Basic)

Package-level dependency analysis:

### Features
- **Package Dependencies**: Import relationship tracking
- **Module Boundaries**: Package organization understanding
- **Standard Library**: Go standard package recognition

### Example Output
```json
{
  "path": "internal/models/user.go",
  "language": "go",
  "dependencies": ["fmt", "encoding/json", "./database"],
  "imports": [
    "import \"fmt\"",
    "import \"encoding/json\"", 
    "import \"./database\""
  ],
  "loc": 234
}
```

## Roadmap

### Near-term Enhancements (Next Release)

#### **JavaScript/TypeScript**
- Function and class symbol extraction
- ES6+ feature detection (async/await, destructuring)
- Framework pattern recognition (React, Vue, Angular)
- Bundle analysis integration

#### **Go**
- Function and struct analysis
- Interface implementation tracking
- Goroutine usage detection
- Module dependency depth analysis

### Medium-term Additions

#### **Rust**
- Ownership and borrowing analysis
- Trait implementation tracking
- Macro usage detection
- Crate dependency mapping

#### **Java**
- Class hierarchy analysis
- Annotation processing
- Spring framework patterns
- Maven/Gradle integration

#### **C#**
- Namespace and assembly analysis
- LINQ usage patterns
- .NET framework integration
- NuGet dependency tracking

### Long-term Vision

#### **Language-Agnostic Features**
- Cross-language dependency tracking
- Polyglot project analysis
- Universal design pattern detection
- Architecture compliance checking

## Usage by Language

### Python Projects
```bash
# Full analysis with all features
intentgraph . --lang python --level full

# AI-optimized clustering for large Python codebases
intentgraph . --lang python --cluster --cluster-mode analysis
```

### JavaScript/TypeScript Projects
```bash
# Basic dependency analysis
intentgraph . --lang js,ts --level minimal

# Focus on module relationships
intentgraph . --lang js,ts --cluster --cluster-mode navigation
```

### Go Projects
```bash
# Package-level analysis
intentgraph . --lang go --level minimal

# Module organization clustering
intentgraph . --lang go --cluster --cluster-mode refactoring
```

### Mixed Language Projects
```bash
# Analyze all supported languages
intentgraph . --lang py,js,ts,go

# Create language-aware clusters
intentgraph . --cluster --cluster-mode analysis
```

## Implementation Details

### Parser Architecture
Each language has a dedicated parser implementing the `LanguageParser` interface:

```python
class LanguageParser(ABC):
    @abstractmethod
    def extract_code_structure(self, file_path: Path) -> CodeStructure:
        """Extract structure from source file."""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Return file extensions this parser supports."""
        pass
```

### Enhancement Strategy
Language support enhancement follows this priority:

1. **File Dependencies**: Basic import/module tracking
2. **Symbol Extraction**: Functions, classes, variables
3. **Quality Metrics**: Complexity and maintainability
4. **Framework Patterns**: Language-specific patterns
5. **Deep Analysis**: Advanced semantic understanding

### Contributing Language Support

To add or enhance language support:

1. **Create Parser**: Implement `LanguageParser` for the target language
2. **Add Tests**: Comprehensive test suite for the new parser
3. **Update Documentation**: Language support matrix and examples
4. **Submit PR**: With parser, tests, and documentation

Example parser structure:
```python
class RustParser(LanguageParser):
    def extract_code_structure(self, file_path: Path) -> CodeStructure:
        # Parse Rust source using tree-sitter or similar
        # Extract functions, structs, traits, etc.
        # Build dependency relationships
        pass
    
    def get_supported_extensions(self) -> List[str]:
        return [".rs"]
```

## Language-Specific Considerations

### Python Best Practices
- **Virtual Environments**: IntentGraph respects activated environments
- **Package Structure**: Understands `__init__.py` and package hierarchies
- **Framework Detection**: Recognizes Django, Flask, FastAPI patterns
- **Testing Integration**: Identifies pytest, unittest patterns

### JavaScript/TypeScript Best Practices
- **Node Modules**: Filters out `node_modules` by default
- **Build Artifacts**: Ignores `dist/`, `build/` directories
- **Framework Support**: Plans for React, Vue, Angular recognition
- **Monorepo Handling**: Understands workspace structures

### Go Best Practices
- **Module System**: Respects `go.mod` boundaries
- **Package Naming**: Follows Go package conventions
- **Standard Library**: Distinguishes standard vs. third-party packages
- **Build Tags**: Plans for conditional compilation support

This language support matrix helps users understand current capabilities and plan for future enhancements based on their technology stack.