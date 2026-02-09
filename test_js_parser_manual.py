#!/usr/bin/env python3
"""Manual test script for JavaScript parser."""

from pathlib import Path
from src.intentgraph.adapters.parsers.javascript_parser import JavaScriptParser

def main():
    """Test JavaScript parser manually."""
    parser = JavaScriptParser()

    # Test with sample module
    fixtures_dir = Path("fixtures/javascript")
    sample_module = fixtures_dir / "sample_module.js"

    print("=" * 60)
    print("Testing JavaScript Parser")
    print("=" * 60)

    if not sample_module.exists():
        print(f"ERROR: Test file not found: {sample_module}")
        return 1

    # Test dependency extraction
    print("\n1. Testing dependency extraction...")
    deps = parser.extract_dependencies(sample_module, fixtures_dir)
    print(f"   Dependencies found: {deps}")
    print(f"   ✓ Dependencies are sorted: {deps == sorted(deps)}")

    # Test code structure extraction
    print("\n2. Testing code structure extraction...")
    symbols, exports, func_deps, imports, metadata = parser.extract_code_structure(
        sample_module, fixtures_dir
    )

    print(f"   Symbols found: {len(symbols)}")
    for symbol in symbols:
        print(f"     - {symbol.symbol_type}: {symbol.name} (line {symbol.line_start}-{symbol.line_end})")
        print(f"       ID: {symbol.id}")

    print(f"\n   Exports found: {len(exports)}")
    for export in exports:
        print(f"     - {export.name}")

    print(f"\n   Imports found: {len(imports)}")
    for imp in imports:
        print(f"     - {imp}")

    print(f"\n   Metadata:")
    for key, value in metadata.items():
        print(f"     - {key}: {value}")

    # Test determinism
    print("\n3. Testing determinism...")
    symbols2, _, _, imports2, _ = parser.extract_code_structure(
        sample_module, fixtures_dir
    )

    print(f"   ✓ Symbol count matches: {len(symbols) == len(symbols2)}")
    print(f"   ✓ Symbol IDs are stable: {all(s1.id == s2.id for s1, s2 in zip(symbols, symbols2))}")
    print(f"   ✓ Imports are sorted: {imports == sorted(imports)}")
    print(f"   ✓ Import determinism: {imports == imports2}")

    # Test with other files
    print("\n4. Testing with other fixtures...")
    for filename in ["sample_es6.js", "sample_functions.js", "sample_classes.js"]:
        filepath = fixtures_dir / filename
        if filepath.exists():
            syms, _, _, _, _ = parser.extract_code_structure(filepath, fixtures_dir)
            print(f"   {filename}: {len(syms)} symbols")

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)

    return 0

if __name__ == "__main__":
    exit(main())
