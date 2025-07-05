# IntentGraph Architecture

## Overview

IntentGraph follows Clean Architecture principles, ensuring separation of concerns and maintainability. The system is designed as a modular, testable, and extensible dependency analyzer.

## Architecture Layers

### 1. CLI Layer (`intentgraph.cli`)
- **Purpose**: Command-line interface and user interaction
- **Technologies**: Typer, Rich Console
- **Responsibilities**:
  - Parse command-line arguments
  - Configure logging and output
  - Handle user feedback and progress display
  - Orchestrate application layer calls

### 2. Application Layer (`intentgraph.application`)
- **Purpose**: Business logic orchestration
- **Technologies**: Python standard library, concurrent.futures
- **Responsibilities**:
  - Coordinate repository scanning
  - Manage parallel processing
  - Build dependency graphs
  - Generate analysis results

### 3. Domain Layer (`intentgraph.domain`)
- **Purpose**: Core business entities and rules
- **Technologies**: Pydantic, dataclasses
- **Responsibilities**:
  - Define core entities (FileInfo, Language, AnalysisResult)
  - Implement graph operations and cycle detection
  - Define business rules and invariants
  - Handle domain-specific exceptions

### 4. Infrastructure Layer (`intentgraph.adapters`)
- **Purpose**: External integrations and technical concerns
- **Technologies**: pathspec, grimp, tree-sitter, NetworkX
- **Responsibilities**:
  - Git integration and .gitignore handling
  - Language-specific parsing
  - File system operations
  - JSON serialization and validation

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                           CLI Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  • typer.App                                                    │
│  • Rich Console                                                 │
│  • Argument parsing                                             │
│  • Progress display                                             │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  • RepositoryAnalyzer                                           │
│  • Parallel processing orchestration                           │
│  • File discovery and filtering                                │
│  • Dependency graph construction                               │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Domain Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  • FileInfo, Language, AnalysisResult                          │
│  • DependencyGraph                                             │
│  • Business rules and validations                              │
│  • Cycle detection algorithms                                  │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Git Adapter   │  │   Parsers       │  │   Output        │  │
│  │                 │  │                 │  │                 │  │
│  │ • GitIgnore     │  │ • PythonParser  │  │ • JSONFormatter │  │
│  │   Handler       │  │ • JSParser      │  │ • Schema        │  │
│  │ • pathspec      │  │ • TSParser      │  │   Validator     │  │
│  │ • GitPython     │  │ • GoParser      │  │ • orjson        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Input Processing**: CLI layer parses arguments and validates repository path
2. **Repository Scanning**: Application layer discovers files using Git adapter
3. **Parallel Analysis**: Files are analyzed in parallel using language-specific parsers
4. **Graph Construction**: Domain layer builds dependency graph from analysis results
5. **Cycle Detection**: NetworkX algorithms identify circular dependencies
6. **Output Generation**: Results are formatted and validated before output

## Key Design Decisions

### Clean Architecture Benefits
- **Independence**: Business logic is isolated from frameworks and external concerns
- **Testability**: Each layer can be tested in isolation
- **Flexibility**: Easy to swap implementations (e.g., different parsers)
- **Maintainability**: Clear separation of concerns

### Language Parser Strategy
- **Plugin Architecture**: Each language has its own parser implementing `LanguageParser`
- **Battle-tested Libraries**: Use mature, actively maintained parsing libraries
- **Graceful Degradation**: Fallback mechanisms for parsing failures

### Performance Optimizations
- **Parallel Processing**: Multi-core file analysis using ProcessPoolExecutor
- **Memory Efficiency**: Stream processing for large repositories
- **Caching Strategy**: SHA256 hashing for file change detection

### Error Handling
- **Fail Fast**: Validate inputs early and provide clear error messages
- **Graceful Degradation**: Continue analysis even if some files fail
- **Comprehensive Logging**: Rich logging for debugging and monitoring

## Extension Points

### Adding New Languages
1. Implement `LanguageParser` interface
2. Add language to `Language` enum
3. Register parser in parser factory
4. Add tests for new parser

### Custom Output Formats
1. Implement new formatter in `adapters.output`
2. Add format option to CLI
3. Extend validation schema if needed

### Additional Graph Operations
1. Add methods to `DependencyGraph` class
2. Implement using NetworkX algorithms
3. Add corresponding CLI flags

## Security Considerations

- **Input Validation**: All file paths are validated and sanitized
- **Sandboxing**: Subprocess calls are properly isolated
- **No Code Execution**: Static analysis only, no dynamic code execution
- **Resource Limits**: Timeouts and memory limits for analysis operations

## Testing Strategy

- **Unit Tests**: Each component tested in isolation
- **Integration Tests**: End-to-end workflow testing
- **Property-based Testing**: Hypothesis for edge cases
- **Performance Tests**: Benchmarks for large repositories
- **Security Tests**: Bandit for vulnerability scanning

## Dependencies

### Core Dependencies
- **typer**: Modern CLI framework
- **rich**: Terminal formatting and progress bars
- **pathspec**: Git-compatible .gitignore parsing
- **pydantic**: Data validation and serialization
- **networkx**: Graph algorithms and operations
- **orjson**: Fast JSON serialization

### Language-specific Dependencies
- **grimp**: Python import graph analysis
- **tree-sitter**: Multi-language parsing
- **tree-sitter-languages**: Language grammars

### Development Dependencies
- **pytest**: Testing framework
- **mypy**: Static type checking
- **ruff**: Fast linting and formatting
- **bandit**: Security vulnerability detection

This architecture ensures IntentGraph remains maintainable, testable, and extensible while providing excellent performance and reliability.