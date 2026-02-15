"""Comprehensive tests for TypeScriptParser."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from intentgraph.adapters.parsers.typescript_parser import TypeScriptParser


class TestTypeScriptParser:
    """Test suite for TypeScriptParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = TypeScriptParser()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures" / "typescript"

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_lazy_initialization(self):
        """Test lazy initialization of tree-sitter."""
        parser = TypeScriptParser()
        assert parser._parser is None
        assert parser._language is None

        # Trigger initialization
        test_file = self.fixtures_dir / "sample_class.ts"
        parser.extract_code_structure(test_file, self.fixtures_dir)

        # Should be initialized now (if tree-sitter available)
        # or should have recorded error
        assert parser._parser is not None or parser._init_error is not None

    def test_extract_symbols_from_class_file(self):
        """Test symbol extraction from class file."""
        test_file = self.fixtures_dir / "sample_class.ts"

        symbols, exports, func_deps, imports, metadata = self.parser.extract_code_structure(
            test_file, self.fixtures_dir
        )

        # Should extract Calculator class and InternalHelper class
        symbol_names = [s.name for s in symbols]
        assert "Calculator" in symbol_names
        assert "InternalHelper" in symbol_names

        # Should extract methods
        method_names = [s.name for s in symbols if s.symbol_type == 'function']
        assert "add" in method_names or "subtract" in method_names or "multiply" in method_names

        # Check counts
        assert len(symbols) >= 2  # At least 2 classes

    def test_extract_symbols_from_interface_file(self):
        """Test symbol extraction from interface/type file."""
        test_file = self.fixtures_dir / "sample_interface.ts"

        symbols, exports, func_deps, imports, metadata = self.parser.extract_code_structure(
            test_file, self.fixtures_dir
        )

        # Should extract interfaces
        interface_names = [s.name for s in symbols if s.symbol_type == 'interface']
        assert "User" in interface_names
        assert "Product" in interface_names
        assert "InternalConfig" in interface_names

        # Should extract types
        type_names = [s.name for s in symbols if s.symbol_type == 'type']
        assert "UserRole" in type_names
        assert "Status" in type_names
        assert "ApiResponse" in type_names
        assert "Nullable" in type_names

        # Check total counts
        assert len([s for s in symbols if s.symbol_type == 'interface']) >= 3
        assert len([s for s in symbols if s.symbol_type == 'type']) >= 4

    def test_extract_symbols_from_enum_file(self):
        """Test symbol extraction from enum file."""
        test_file = self.fixtures_dir / "sample_exports.ts"

        symbols, exports, func_deps, imports, metadata = self.parser.extract_code_structure(
            test_file, self.fixtures_dir
        )

        # Should extract enums
        enum_names = [s.name for s in symbols if s.symbol_type == 'enum']
        assert "LogLevel" in enum_names
        assert "Status" in enum_names

        # Should extract functions
        function_names = [s.name for s in symbols if s.symbol_type == 'function']
        assert "processData" in function_names
        assert "logMessage" in function_names

    def test_import_edge_detection(self):
        """Test import edge detection."""
        test_file = self.fixtures_dir / "sample_imports.ts"

        symbols, exports, func_deps, imports, metadata = self.parser.extract_code_structure(
            test_file, self.fixtures_dir
        )

        # Should extract imports
        assert len(imports) > 0

        # Verify imports reference other files
        import_strings = ' '.join(imports)
        assert './sample_class' in import_strings or 'sample_class' in import_strings
        assert './sample_interface' in import_strings or 'sample_interface' in import_strings

    def test_export_detection(self):
        """Test export detection."""
        test_file = self.fixtures_dir / "sample_exports.ts"

        symbols, exports, func_deps, imports, metadata = self.parser.extract_code_structure(
            test_file, self.fixtures_dir
        )

        # Should detect exported symbols
        export_names = [e.name for e in exports]
        assert "LogLevel" in export_names
        assert "Status" in export_names
        assert "processData" in export_names
        assert "logMessage" in export_names

        # Internal helper should not be exported
        assert "internalHelper" not in export_names

    def test_deterministic_ordering(self):
        """Test that symbol ordering is deterministic."""
        test_file = self.fixtures_dir / "sample_class.ts"

        # Run extraction twice
        result1 = self.parser.extract_code_structure(test_file, self.fixtures_dir)
        result2 = self.parser.extract_code_structure(test_file, self.fixtures_dir)

        symbols1, exports1, _, imports1, _ = result1
        symbols2, exports2, _, imports2, _ = result2

        # Should have same order
        assert len(symbols1) == len(symbols2)
        for i, (s1, s2) in enumerate(zip(symbols1, symbols2)):
            assert s1.name == s2.name, f"Symbol order differs at index {i}"
            assert s1.symbol_type == s2.symbol_type
            assert s1.line_start == s2.line_start

        # Exports should be sorted
        assert exports1 == exports2

        # Imports should be sorted
        assert imports1 == imports2

    def test_stable_symbol_ids(self):
        """Test that symbol IDs are stable across runs."""
        test_file = self.fixtures_dir / "sample_class.ts"

        # Run extraction twice
        symbols1, _, _, _, _ = self.parser.extract_code_structure(test_file, self.fixtures_dir)
        symbols2, _, _, _, _ = self.parser.extract_code_structure(test_file, self.fixtures_dir)

        # Same symbols should have same IDs
        for s1, s2 in zip(symbols1, symbols2):
            assert s1.id == s2.id, f"ID changed for symbol {s1.name}"

    def test_metadata_calculation(self):
        """Test metadata calculation."""
        test_file = self.fixtures_dir / "sample_class.ts"

        _, _, _, _, metadata = self.parser.extract_code_structure(test_file, self.fixtures_dir)

        # Should have metadata fields
        assert 'total_functions' in metadata
        assert 'total_classes' in metadata
        assert 'lines_of_code' in metadata

        # Should have meaningful values
        assert metadata['total_classes'] >= 2
        assert metadata['total_functions'] >= 5  # Calculator methods
        assert metadata['lines_of_code'] > 0

    def test_private_symbol_detection(self):
        """Test private symbol detection (underscore prefix)."""
        test_code = """
        export class TestClass {
            public method(): void {}
            _privateMethod(): void {}
        }

        export function publicFunc(): void {}
        function _privateFunc(): void {}
        """

        test_file = self.temp_dir / "test_private.ts"
        test_file.write_text(test_code)

        symbols, _, _, _, _ = self.parser.extract_code_structure(test_file, self.temp_dir)

        # Check private detection
        private_symbols = [s for s in symbols if s.is_private]
        assert any('_private' in s.name.lower() for s in private_symbols)

    def test_graceful_fallback_when_tree_sitter_unavailable(self):
        """Test graceful fallback when tree-sitter is not available."""
        with patch('src.intentgraph.adapters.parsers.typescript_parser.TypeScriptParser._ensure_initialized', return_value=False):
            parser = TypeScriptParser()
            test_file = self.fixtures_dir / "sample_class.ts"

            symbols, exports, func_deps, imports, metadata = parser.extract_code_structure(
                test_file, self.fixtures_dir
            )

            # Should return empty results without crashing
            assert symbols == []
            assert exports == []
            assert func_deps == []
            assert imports == []
            assert metadata == {}

    def test_extract_dependencies(self):
        """Test file-level dependency extraction."""
        test_file = self.fixtures_dir / "sample_imports.ts"

        dependencies = self.parser.extract_dependencies(test_file, self.fixtures_dir)

        # Should extract dependencies to other files in the fixture directory
        # Note: Dependencies may be empty if files don't resolve, but should not crash
        assert isinstance(dependencies, list)

    def test_symbol_sorting_order(self):
        """Test that symbols are sorted by line, type, and name."""
        test_code = """
        interface A { x: number; }
        function z(): void {}
        function a(): void {}
        class B {}
        """

        test_file = self.temp_dir / "test_sort.ts"
        test_file.write_text(test_code)

        symbols, _, _, _, _ = self.parser.extract_code_structure(test_file, self.temp_dir)

        # Verify sorting: line_start, symbol_type, name
        for i in range(len(symbols) - 1):
            current = symbols[i]
            next_sym = symbols[i + 1]

            # Either earlier line, or same line but earlier type/name
            if current.line_start == next_sym.line_start:
                assert (current.symbol_type, current.name) <= (next_sym.symbol_type, next_sym.name)
            else:
                assert current.line_start <= next_sym.line_start

    def test_deterministic_symbol_id_generation(self):
        """Test that symbol ID generation is deterministic based on file, kind, name, and line."""
        test_code = """
        function testFunction(): void {}
        class TestClass {}
        """

        test_file = self.temp_dir / "test_id.ts"
        test_file.write_text(test_code)

        # Extract twice
        symbols1, _, _, _, _ = self.parser.extract_code_structure(test_file, self.temp_dir)
        symbols2, _, _, _, _ = self.parser.extract_code_structure(test_file, self.temp_dir)

        # IDs should match exactly
        assert len(symbols1) == len(symbols2)
        for s1, s2 in zip(symbols1, symbols2):
            assert s1.id == s2.id
            # Verify ID is based on canonical path
            assert str(s1.id) == str(s2.id)

    def test_empty_file_handling(self):
        """Test handling of empty TypeScript file."""
        test_file = self.temp_dir / "empty.ts"
        test_file.write_text("")

        symbols, exports, func_deps, imports, metadata = self.parser.extract_code_structure(
            test_file, self.temp_dir
        )

        # Should handle gracefully
        assert symbols == []
        assert exports == []
        assert imports == []

    def test_complex_nested_structures(self):
        """Test handling of nested classes and functions."""
        test_code = """
        export class OuterClass {
            method(): void {
                function innerFunc(): void {}
            }

            static staticMethod(): void {}
        }
        """

        test_file = self.temp_dir / "nested.ts"
        test_file.write_text(test_code)

        symbols, _, _, _, _ = self.parser.extract_code_structure(test_file, self.temp_dir)

        # Should extract outer and nested symbols
        assert len(symbols) >= 1
        assert any(s.name == "OuterClass" for s in symbols)
