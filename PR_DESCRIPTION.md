# Add enhanced JavaScript and TypeScript parsers with full AST analysis

## Summary

Adds full AST parsing support for JavaScript and TypeScript, elevating them from basic file-level dependency tracking to comprehensive code analysis on par with Python support.

## What's New

### JavaScript Parser (`javascript_parser.py`)
- ✅ Full AST parsing using tree-sitter
- ✅ Class and function extraction with signatures
- ✅ ES6+ support (arrow functions, destructuring, template literals)
- ✅ Import/export analysis (CommonJS and ES modules)
- ✅ Cyclomatic complexity calculation
- ✅ Public API detection
- ✅ 301 comprehensive tests with fixtures

### TypeScript Parser (`typescript_parser.py`)
- ✅ Full AST parsing with TypeScript-specific features
- ✅ Interface and type alias extraction
- ✅ Generic type parameter handling
- ✅ Decorator support
- ✅ Import/export analysis (including type imports)
- ✅ Cyclomatic complexity calculation
- ✅ 316 comprehensive tests with fixtures

## Language Support Update

| Language   | Before | After |
|------------|--------|-------|
| Python | ✅ Full | ✅ Full |
| **JavaScript** | 🟡 Basic | ✅ **Full** |
| **TypeScript** | 🟡 Basic | ✅ **Full** |
| Go | 🟡 Basic | 🟡 Basic |

## Test Coverage

- **JavaScript**: 301 tests across multiple fixture files
  - `sample_classes.js` - Class extraction and methods
  - `sample_es6.js` - Modern JavaScript features
  - `sample_functions.js` - Function parsing and complexity
  - `sample_module.js` - Import/export handling

- **TypeScript**: 316 tests across multiple fixture files
  - `sample_class.ts` - Class with decorators and generics
  - `sample_exports.ts` - Various export patterns
  - `sample_imports.ts` - Import statement handling
  - `sample_interface.ts` - Interface and type definitions

## Example Output

### JavaScript Analysis
```json
{
  "path": "src/api.js",
  "language": "javascript",
  "symbols": [
    {
      "name": "UserService",
      "symbol_type": "class",
      "line_start": 10,
      "line_end": 45,
      "is_exported": true
    },
    {
      "name": "createUser",
      "symbol_type": "function",
      "signature": "async createUser(userData)",
      "complexity_score": 4
    }
  ],
  "exports": ["UserService", "createUser"],
  "imports": ["express", "./models/User"],
  "complexity_score": 12
}
```

### TypeScript Analysis
```json
{
  "path": "src/services.ts",
  "language": "typescript",
  "symbols": [
    {
      "name": "IUserService",
      "symbol_type": "interface",
      "is_exported": true
    },
    {
      "name": "UserService",
      "symbol_type": "class",
      "signature": "class UserService implements IUserService",
      "decorators": ["Injectable"]
    }
  ],
  "exports": ["IUserService", "UserService"],
  "imports": ["@nestjs/common", "./interfaces"],
  "complexity_score": 8
}
```

## Breaking Changes

None - this is purely additive functionality.

## CLI Usage

```bash
# Analyze JavaScript projects
intentgraph /path/to/js-project --lang js

# Analyze TypeScript projects
intentgraph /path/to/ts-project --lang ts

# Mixed language analysis
intentgraph /path/to/fullstack --lang py,js,ts
```

## Documentation Updates Needed

After merge, we should update:
- [ ] README.md language support table (already updated in branch)
- [ ] Language support documentation
- [ ] Examples showing JS/TS analysis

## Testing

All tests pass:
```bash
pytest tests/test_javascript_parser.py -v  # 301 tests
pytest tests/test_typescript_parser.py -v  # 316 tests
```

## Related Issues

Addresses #1 (language support expansion)

🤖 Generated with Claude Code
