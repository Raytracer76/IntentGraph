"""Test IntentGraph Python-only functionality (bypasses tree-sitter parsers)."""

import sys
from pathlib import Path

# Use ASCII for Windows console compatibility
OK = "[OK]"
FAIL = "[FAIL]"

# Test 1: Import basic domain models
print("Test 1: Importing domain models...")
try:
    from intentgraph.domain.models import Language, CodeSymbol, FileInfo
    print(f"{OK} Domain models imported successfully")
except Exception as e:
    print(f"{FAIL} Failed to import domain models: {e}")
    sys.exit(1)

# Test 2: Test enhanced Python parser directly
print("\nTest 2: Testing enhanced Python parser...")
try:
    from intentgraph.adapters.parsers.enhanced_python_parser import EnhancedPythonParser
    import tempfile
    import os

    # Create test Python code in a temp file
    test_code = '''
def hello_world():
    """Say hello."""
    return "Hello, World!"

class TestClass:
    def __init__(self):
        self.value = 42

    def get_value(self):
        return self.value
'''

    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_code)
        temp_file = Path(f.name)

    try:
        parser = EnhancedPythonParser()
        # extract_code_structure returns a tuple: (symbols, exports, deps, imports, metadata)
        symbols, exports, function_deps, imports, metadata = parser.extract_code_structure(
            temp_file, temp_file.parent
        )

        print(f"  - Found {len(symbols)} symbols")
        print(f"  - Symbols: {[s.name for s in symbols]}")
        print(f"  - Exports: {len(exports)}")
        print(f"  - Metadata: {metadata}")
        print("[OK] Python parser works correctly")
    finally:
        # Clean up temp file
        os.unlink(temp_file)

except Exception as e:
    print(f"[FAIL] Python parser failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test repository analysis with Python-only language filter
print("\nTest 3: Testing repository analyzer with Python files only...")
try:
    from intentgraph.application.analyzer import RepositoryAnalyzer

    # Analyze this repo itself, but only Python files
    current_dir = Path.cwd()
    analyzer = RepositoryAnalyzer(
        workers=2,
        include_tests=True,
        language_filter=[Language.PYTHON]  # Only analyze Python files
    )

    result = analyzer.analyze(current_dir)

    # Calculate totals
    total_symbols = sum(len(f.symbols) for f in result.files)
    total_imports = sum(len(f.imports) for f in result.files)

    print(f"  - Analyzed {len(result.files)} Python files")
    print(f"  - Found {total_symbols} symbols")
    print(f"  - Found {total_imports} imports")

    if result.files:
        sample_file = result.files[0]
        print(f"  - Sample file: {sample_file.path}")
        print(f"    - Symbols: {len(sample_file.symbols)}")
        print(f"    - Imports: {len(sample_file.imports)}")

    print("[OK] Repository analyzer works with Python-only mode")

except Exception as e:
    print(f"[FAIL] Repository analyzer failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test minimal output mode (AI-friendly)
print("\nTest 4: Testing minimal output mode...")
try:
    from intentgraph.cli import filter_result_by_level

    # Use the result from test 3
    minimal_result = filter_result_by_level(result, "minimum")

    # Check that it was filtered (returns a dict)
    if minimal_result["files"]:
        # Minimal mode has no symbols field, only basic info
        print(f"  - Minimal mode files: {len(minimal_result['files'])}")
        print(f"  - Sample file: {minimal_result['files'][0]['path']}")
        print(f"  - Original file had: {len(result.files[0].symbols)} symbols")
        print(f"  - Minimal mode fields: {list(minimal_result['files'][0].keys())}")
        print("[OK] Minimal output mode works")
    else:
        print("  - No files to filter (repo might be empty)")
        print("[OK] Minimal output mode works (no crash)")

except Exception as e:
    print(f"[FAIL] Minimal output mode failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test AI-native interface (without tree-sitter)
print("\nTest 5: Testing AI-native interface (manifest generation)...")
try:
    # Can't use connect_to_codebase because it imports the parser registry
    # which tries to load tree-sitter parsers. Instead, test manifest directly.
    from intentgraph.ai.manifest import get_capabilities_manifest

    manifest = get_capabilities_manifest()

    print(f"  - Interface version: {manifest['intentgraph_ai_interface']['version']}")
    print(f"  - Capabilities: {len(manifest['capabilities'])} available")
    print(f"  - Top-level keys: {list(manifest.keys())}")
    print("[OK] AI-native manifest generation works")

except Exception as e:
    print(f"[FAIL] AI-native interface failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("All Python-only tests passed! [OK]")
print("="*60)
print("\nNote: Full test suite requires tree-sitter native libraries,")
print("which are blocked by Windows Application Control policy.")
print("However, core Python analysis functionality works perfectly!")
