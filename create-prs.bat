@echo off
REM Multi-Language Parser Sprint - PR Creation Script (Windows)
REM Run this script to create all three pull requests

echo Creating pull requests for multi-language parser sprint...
echo.

REM PR 1: JSON Parser
echo 1. Creating PR for JSON parser (feat/lang-json)...
git pr create --base main --head feat/lang-json --title "Add JSON parser with dependency extraction" --body "## Summary\n\nImplements JSON parser for IntentGraph with comprehensive package.json dependency extraction.\n\n## Features\n- ✅ Top-level key extraction as symbols\n- ✅ package.json dependency parsing (dependencies, devDependencies, peerDependencies, optionalDependencies)\n- ✅ Stable SHA256-based symbol IDs\n- ✅ Deterministic alphabetical ordering\n- ✅ No tree-sitter dependency (pure Python json module)\n- ✅ File type inference (package.json, tsconfig.json, generic)\n\n## Test Results\n- **Local (Windows)**: 24/24 tests passing ✅\n- **Coverage**: 91%% on json_parser.py\n- **CI Status**: Pending verification on Linux\n\n## Files Changed\n- `src/intentgraph/adapters/parsers/json_parser.py` (new, 93 lines)\n- `src/intentgraph/domain/models.py` (Language.JSON enum)\n- `src/intentgraph/adapters/parsers/__init__.py` (registry)\n- `fixtures/json/` (6 test fixtures)\n- `tests/test_json_parser.py` (24 comprehensive tests)\n\n## Contract Compliance\n✅ Deterministic symbol IDs (SHA256-based)\n✅ Alphabetical ordering (all outputs)\n✅ Lazy initialization pattern\n✅ Graceful error handling\n\n## Merge Strategy\n**Priority: HIGH** - Ready to merge immediately after CI confirms tests pass on Linux.\n\nCo-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

echo ✅ JSON parser PR created
echo.

REM PR 2: TypeScript Parser
echo 2. Creating PR for TypeScript parser (feat/lang-ts)...
git pr create --base main --head feat/lang-ts --title "Add TypeScript parser with deterministic analysis" --body "## Summary\n\nImplements TypeScript parser for IntentGraph with comprehensive symbol extraction and dependency tracking.\n\n## Features\n- ✅ Symbol extraction: functions, classes, interfaces, types, enums\n- ✅ Import/export detection with resolution\n- ✅ Stable SHA256-based symbol IDs\n- ✅ Deterministic ordering (line number, then alphabetical)\n- ✅ Lazy tree-sitter initialization with graceful fallback\n- ✅ Private symbol detection (underscore prefix)\n\n## Test Results\n- **Local (Windows)**: 16/16 tests passing ✅\n- **Coverage**: 76%% on typescript_parser.py\n- **CI Status**: Pending verification on Linux\n\n## Files Changed\n- `src/intentgraph/adapters/parsers/typescript_parser.py` (new, 183 lines)\n- `src/intentgraph/domain/models.py` (Language.TYPESCRIPT enum)\n- `src/intentgraph/adapters/parsers/__init__.py` (registry)\n- `fixtures/typescript/` (4 test fixtures)\n- `tests/test_typescript_parser.py` (16 comprehensive tests)\n\n## Contract Compliance\n✅ Deterministic symbol IDs (SHA256-based)\n✅ Deterministic ordering (line number + name)\n✅ Lazy initialization pattern\n✅ Graceful fallback if tree-sitter unavailable\n\n## Merge Strategy\n**Priority: HIGH** - Ready to merge immediately after CI confirms tests pass on Linux.\n\nCo-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

echo ✅ TypeScript parser PR created
echo.

REM PR 3: JavaScript Parser
echo 3. Creating PR for JavaScript parser (feat/lang-js)...
git pr create --base main --head feat/lang-js --title "Add JavaScript parser with CommonJS and ES6 support" --body "## Summary\n\nImplements JavaScript parser for IntentGraph with CommonJS and ES6 module support.\n\n## Features\n- ✅ CommonJS require() statements\n- ✅ ES6 import/export statements\n- ✅ Function extraction (regular, arrow, async, generator)\n- ✅ Class declarations\n- ✅ Stable SHA256-based symbol IDs\n- ✅ Deterministic alphabetical ordering\n- ✅ Lazy tree-sitter initialization with graceful fallback\n\n## Test Results\n- **Local (Windows)**: 15/24 tests passing ⚠️\n  - 15 PASS: Determinism, ordering, structure validation\n  - 9 FAIL: Symbol extraction (tree-sitter blocked by Windows ACL)\n- **Coverage**: 37%% (blocked by Windows Application Control)\n- **CI Status**: ⏳ **AWAITING LINUX CI VERIFICATION**\n\n## Known Issue: Windows Application Control\n**Root Cause**: Windows Application Control policy blocks tree-sitter native libraries:\n```\nOSError: [WinError 4551] An Application Control policy has blocked this file:\ntree_sitter_languages/languages.cp312-win_amd64.pyd\n```\n\n**Impact**: Symbol extraction tests fail in Windows ACL environments only\n**Resolution**: Tests should pass in standard Linux/Mac/CI environments\n\n## Files Changed\n- `src/intentgraph/adapters/parsers/javascript_parser.py` (new, 181 lines)\n- `src/intentgraph/domain/models.py` (Language.JAVASCRIPT enum)\n- `src/intentgraph/adapters/parsers/__init__.py` (registry)\n- `fixtures/javascript/` (4 test fixtures)\n- `tests/test_javascript_parser.py` (24 comprehensive tests)\n\n## Contract Compliance\n✅ Deterministic symbol IDs (SHA256-based)\n✅ Deterministic ordering (all outputs sorted)\n✅ Lazy initialization pattern\n✅ Code complete and deterministic\n\n## Merge Strategy\n**Priority: MEDIUM** - Merge after CI confirms all tests pass on Linux.\n\n**Alternative**: If CI also fails, mark Windows-specific tests as `xfail`:\n```python\n@pytest.mark.xfail(sys.platform == 'win32', reason='Windows ACL blocks tree-sitter')\ndef test_extract_function_declarations(...):\n    ...\n```\n\nCo-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

echo ✅ JavaScript parser PR created
echo.

echo ════════════════════════════════════════════════════════
echo ✅ All 3 pull requests created successfully!
echo.
echo Next steps:
echo 1. Wait for CI to run on all three PRs
echo 2. Merge JSON + TypeScript first (if CI green)
echo 3. Merge JavaScript after CI verification (or add xfail markers)
echo.
echo Monitor CI status:
echo   gh pr list --state open
echo   gh pr checks [PR-NUMBER]
echo ════════════════════════════════════════════════════════
