# Changelog

All notable changes to IntentGraph will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2025-07-06

### Added
- **🧩 Intelligent Clustering System**: Revolutionary approach for large codebase navigation and AI agent optimization
  - `--cluster`: Enable cluster mode for repositories that exceed AI token limits even with minimal output
  - **Three clustering strategies**:
    - `--cluster-mode analysis`: Dependency-based clustering for code understanding (with smart overlap)
    - `--cluster-mode refactoring`: Feature-based clustering for targeted changes (no overlap)
    - `--cluster-mode navigation`: Size-optimized clustering for large repository exploration
  - **Flexible sizing**: `--cluster-size 10KB|15KB|20KB` with intelligent constraint handling
  - **Rich index system**: `--index-level basic|rich` with AI agent recommendations

### Features
- **Smart Clustering Algorithms**: 
  - Dependency-based: Groups files by architectural layers and dependency relationships
  - Feature-based: Groups files by functional domains (parsing, analysis, CLI, models, etc.)
  - Size-optimized: Balances clusters for optimal AI token utilization
- **Intelligent Index Generation**: Master index.json with cluster navigation metadata
- **AI Agent Recommendations**: Pre-computed cluster suggestions for common tasks
  - `understanding_codebase`: High-level architectural clusters
  - `making_changes`: Interface and adapter clusters
  - `finding_bugs`: Complex and utility clusters
  - `adding_features`: Extensible pattern clusters
- **Cross-Cluster Dependencies**: Automatic detection of relationships between clusters
- **Progressive File Output**: Directory structure with index.json + individual cluster files

### Technical Implementation
- **Domain Models**: Complete clustering types with Pydantic validation (`ClusterConfig`, `ClusterIndex`, `ClusterResult`)
- **Clustering Engine**: Pluggable algorithms with size constraint management
- **CLI Integration**: Full parameter validation and rich progress reporting
- **Output Formats**: Both directory structure and stdout index output support

### Benefits for AI Agents
- **Unlimited Repository Size**: Break massive codebases into manageable 10-20KB clusters
- **Smart Navigation**: AI agents use index.json to intelligently select relevant clusters
- **Task-Optimized**: Different clustering modes for different AI workflows
- **Preserves Context**: Smart overlap and dependency tracking maintains code relationships

### Examples and Documentation
- **Comprehensive README**: Updated with clustering documentation and examples
- **Demo Scripts**: 
  - `examples/clustering/large_codebase_navigation.py`: Complete clustering workflow demonstration
  - `examples/clustering/cluster_mode_comparison.py`: Side-by-side mode comparison
  - `examples/clustering/README.md`: Detailed clustering guide with AI integration patterns

### Performance
- **Scalable**: Handles repositories of any size with linear memory usage
- **Deterministic**: Same input produces identical clustering results
- **Efficient**: Adds only 10-20% to analysis time for clustering computation

## [0.2.1] - 2025-07-06

### Added
- **🤖 AI-Optimized Output Levels**: Revolutionary tiered output system for AI agent compatibility
  - `--level minimal`: ~10KB output (perfect for AI agents, **now default**)
  - `--level medium`: ~70KB output (balanced analysis for complex AI tasks)
  - `--level full`: ~340KB output (complete analysis for comprehensive audits)
- **Token Limit Friendly**: Minimal level ensures codebase intelligence fits in any AI context window
- **Smart Filtering**: Intelligent content filtering preserves essential information while dramatically reducing size
- **AI-First Design**: Made minimal output the default for optimal AI agent consumption

### Changed
- **Default behavior**: Changed from full analysis to minimal analysis (97% size reduction)
- **CLI help**: Enhanced with size indicators for AI-friendly guidance
- **Documentation**: Comprehensive updates highlighting AI optimization features
- **Examples**: Added demonstrations of all three output levels

### Technical Details
- Added `filter_result_by_level()` function with progressive filtering logic
- Minimal level includes: paths, dependencies, imports, basic metrics only
- Medium level adds: key symbols (classes/public functions), exports, maintainability scores
- Maintained full backward compatibility with `--level full`

### Impact
- **AI Agents**: Can now consume entire codebase intelligence without token limit issues
- **Developers**: Faster analysis for quick understanding tasks
- **Tools**: Better integration with AI-powered development tools

## [0.2.0] - 2025-07-05

### Added
- **Security Hardening**: Fixed CVE-2024-22190 in GitPython dependency
- **Performance Optimization**: 10x+ improvements through algorithmic enhancements
- **Architecture Modernization**: Service patterns, dependency injection, clean separation
- **Comprehensive Testing**: Test infrastructure for 90%+ coverage target
- **Standards Compliance**: PEP 8 compliance and modern Python practices

### Changed
- Refactored monolithic analyzer into focused services
- Replaced multiple AST traversals with single-pass algorithm
- Enhanced input validation and security measures
- Improved error handling and user experience

### Fixed
- Critical security vulnerabilities
- Performance bottlenecks in large repository analysis
- Code consistency and style violations
- Architecture layer boundary violations

## [0.1.0] - 2025-07-04

### Added
- Initial release of IntentGraph
- Python codebase analysis with deep AST parsing
- Function-level dependency tracking
- Semantic analysis and pattern detection
- Command-line interface with multiple output formats
- Clean architecture with domain/application/adapter layers

### Features
- Multi-language support foundation (Python, JavaScript, TypeScript, Go)
- Rich code structure analysis
- Dependency graph generation
- Quality metrics (complexity, maintainability)
- Export and API surface mapping