# Changelog

All notable changes to IntentGraph will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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