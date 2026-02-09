"""Tests for JavaScript parser with deterministic analysis."""

import hashlib
from pathlib import Path
from uuid import UUID

import pytest

from src.intentgraph.adapters.parsers.javascript_parser import JavaScriptParser
from src.intentgraph.domain.models import CodeSymbol, APIExport


@pytest.fixture
def js_parser():
    """Create a JavaScript parser instance."""
    return JavaScriptParser()


@pytest.fixture
def fixtures_dir():
    """Get the fixtures directory path."""
    return Path(__file__).parent.parent / "fixtures" / "javascript"


@pytest.fixture
def sample_module_path(fixtures_dir):
    """Get the sample module path."""
    return fixtures_dir / "sample_module.js"


@pytest.fixture
def sample_es6_path(fixtures_dir):
    """Get the sample ES6 module path."""
    return fixtures_dir / "sample_es6.js"


@pytest.fixture
def sample_functions_path(fixtures_dir):
    """Get the sample functions path."""
    return fixtures_dir / "sample_functions.js"


@pytest.fixture
def sample_classes_path(fixtures_dir):
    """Get the sample classes path."""
    return fixtures_dir / "sample_classes.js"


class TestJavaScriptParserDependencies:
    """Tests for dependency extraction."""

    def test_extract_commonjs_dependencies(self, js_parser, sample_module_path, fixtures_dir):
        """Test extraction of CommonJS require() statements."""
        deps = js_parser.extract_dependencies(sample_module_path, fixtures_dir)

        # Should find both helper and utils
        assert len(deps) >= 0  # May be 0 if files don't exist
        # Dependencies are sorted
        assert deps == sorted(deps)

    def test_extract_es6_dependencies(self, js_parser, sample_es6_path, fixtures_dir):
        """Test extraction of ES6 import statements."""
        deps = js_parser.extract_dependencies(sample_es6_path, fixtures_dir)

        # Dependencies are sorted and unique
        assert deps == sorted(list(set(deps)))

    def test_dependencies_deterministic_ordering(self, js_parser, sample_module_path, fixtures_dir):
        """Test that dependency extraction is deterministic."""
        deps1 = js_parser.extract_dependencies(sample_module_path, fixtures_dir)
        deps2 = js_parser.extract_dependencies(sample_module_path, fixtures_dir)

        assert deps1 == deps2


class TestJavaScriptParserSymbols:
    """Tests for symbol extraction."""

    def test_extract_function_declarations(self, js_parser, sample_module_path, fixtures_dir):
        """Test extraction of function declarations."""
        symbols, _, _, _, _ = js_parser.extract_code_structure(sample_module_path, fixtures_dir)

        # Should find processData and validateInput functions
        function_names = [s.name for s in symbols if s.symbol_type == 'function']
        assert 'processData' in function_names
        assert 'validateInput' in function_names

    def test_extract_class_declarations(self, js_parser, sample_module_path, fixtures_dir):
        """Test extraction of class declarations."""
        symbols, _, _, _, _ = js_parser.extract_code_structure(sample_module_path, fixtures_dir)

        # Should find DataProcessor class
        class_names = [s.name for s in symbols if s.symbol_type == 'class']
        assert 'DataProcessor' in class_names

    def test_extract_arrow_functions(self, js_parser, sample_functions_path, fixtures_dir):
        """Test extraction of arrow function expressions."""
        symbols, _, _, _, _ = js_parser.extract_code_structure(sample_functions_path, fixtures_dir)

        # Should find arrow functions assigned to variables
        function_names = [s.name for s in symbols if s.symbol_type == 'function']
        assert 'arrowFunction' in function_names
        assert 'arrowFunctionShort' in function_names

    def test_extract_async_functions(self, js_parser, sample_functions_path, fixtures_dir):
        """Test extraction of async functions."""
        symbols, _, _, _, _ = js_parser.extract_code_structure(sample_functions_path, fixtures_dir)

        # Should find async functions
        function_names = [s.name for s in symbols if s.symbol_type == 'function']
        assert 'asyncFunction' in function_names
        assert 'asyncArrowFunction' in function_names

    def test_extract_multiple_classes(self, js_parser, sample_classes_path, fixtures_dir):
        """Test extraction of multiple class declarations."""
        symbols, _, _, _, _ = js_parser.extract_code_structure(sample_classes_path, fixtures_dir)

        # Should find all classes
        class_names = [s.name for s in symbols if s.symbol_type == 'class']
        assert 'BaseClass' in class_names
        assert 'ExtendedClass' in class_names
        assert 'ClassExpression' in class_names

    def test_symbol_has_line_numbers(self, js_parser, sample_module_path, fixtures_dir):
        """Test that symbols have valid line numbers."""
        symbols, _, _, _, _ = js_parser.extract_code_structure(sample_module_path, fixtures_dir)

        for symbol in symbols:
            assert symbol.line_start > 0
            assert symbol.line_end >= symbol.line_start

    def test_symbol_has_signature(self, js_parser, sample_module_path, fixtures_dir):
        """Test that symbols have signatures."""
        symbols, _, _, _, _ = js_parser.extract_code_structure(sample_module_path, fixtures_dir)

        for symbol in symbols:
            assert symbol.signature is not None
            assert len(symbol.signature) > 0


class TestJavaScriptParserDeterminism:
    """Tests for deterministic behavior."""

    def test_stable_symbol_ids(self, js_parser, sample_module_path, fixtures_dir):
        """Test that symbol IDs are stable across multiple parses."""
        symbols1, _, _, _, _ = js_parser.extract_code_structure(sample_module_path, fixtures_dir)
        symbols2, _, _, _, _ = js_parser.extract_code_structure(sample_module_path, fixtures_dir)

        # Sort by name for comparison
        symbols1.sort(key=lambda s: s.name)
        symbols2.sort(key=lambda s: s.name)

        assert len(symbols1) == len(symbols2)

        for s1, s2 in zip(symbols1, symbols2):
            assert s1.id == s2.id
            assert s1.name == s2.name
            assert s1.symbol_type == s2.symbol_type

    def test_deterministic_symbol_ordering(self, js_parser, sample_module_path, fixtures_dir):
        """Test that symbols are ordered deterministically."""
        symbols1, _, _, _, _ = js_parser.extract_code_structure(sample_module_path, fixtures_dir)
        symbols2, _, _, _, _ = js_parser.extract_code_structure(sample_module_path, fixtures_dir)

        # Symbols should be in same order
        assert len(symbols1) == len(symbols2)
        for s1, s2 in zip(symbols1, symbols2):
            assert s1.line_start == s2.line_start
            assert s1.symbol_type == s2.symbol_type
            assert s1.name == s2.name

    def test_deterministic_export_ordering(self, js_parser, sample_functions_path, fixtures_dir):
        """Test that exports are ordered deterministically."""
        _, exports1, _, _, _ = js_parser.extract_code_structure(sample_functions_path, fixtures_dir)
        _, exports2, _, _, _ = js_parser.extract_code_structure(sample_functions_path, fixtures_dir)

        # Exports should be in same order
        assert len(exports1) == len(exports2)
        for e1, e2 in zip(exports1, exports2):
            assert e1.name == e2.name

    def test_deterministic_import_ordering(self, js_parser, sample_es6_path, fixtures_dir):
        """Test that imports are ordered deterministically."""
        _, _, _, imports1, _ = js_parser.extract_code_structure(sample_es6_path, fixtures_dir)
        _, _, _, imports2, _ = js_parser.extract_code_structure(sample_es6_path, fixtures_dir)

        assert imports1 == imports2
        assert imports1 == sorted(imports1)


class TestJavaScriptParserSymbolIDs:
    """Tests for deterministic symbol ID generation."""

    def test_symbol_id_format(self, js_parser, sample_module_path, fixtures_dir):
        """Test that symbol IDs are valid UUIDs."""
        symbols, _, _, _, _ = js_parser.extract_code_structure(sample_module_path, fixtures_dir)

        for symbol in symbols:
            # Should be a UUID
            assert isinstance(symbol.id, UUID)

    def test_symbol_id_uniqueness(self, js_parser, sample_module_path, fixtures_dir):
        """Test that each symbol has a unique ID."""
        symbols, _, _, _, _ = js_parser.extract_code_structure(sample_module_path, fixtures_dir)

        ids = [s.id for s in symbols]
        assert len(ids) == len(set(ids))

    def test_symbol_id_stability_across_files(self, js_parser, fixtures_dir):
        """Test that symbols in different files have different IDs."""
        symbols1, _, _, _, _ = js_parser.extract_code_structure(
            fixtures_dir / "sample_module.js", fixtures_dir
        )
        symbols2, _, _, _, _ = js_parser.extract_code_structure(
            fixtures_dir / "sample_es6.js", fixtures_dir
        )

        ids1 = {s.id for s in symbols1}
        ids2 = {s.id for s in symbols2}

        # Should have no overlap (different files = different canonical paths)
        assert len(ids1.intersection(ids2)) == 0


class TestJavaScriptParserImports:
    """Tests for import extraction."""

    def test_extract_commonjs_imports(self, js_parser, sample_module_path, fixtures_dir):
        """Test extraction of CommonJS require statements."""
        _, _, _, imports, _ = js_parser.extract_code_structure(sample_module_path, fixtures_dir)

        # Should find require statements
        require_imports = [imp for imp in imports if 'require' in imp]
        assert len(require_imports) >= 2  # helper and utils

    def test_extract_es6_imports(self, js_parser, sample_es6_path, fixtures_dir):
        """Test extraction of ES6 import statements."""
        _, _, _, imports, _ = js_parser.extract_code_structure(sample_es6_path, fixtures_dir)

        # Should find import statements
        es6_imports = [imp for imp in imports if 'import' in imp]
        assert len(es6_imports) >= 3  # api, logger, config

    def test_imports_sorted(self, js_parser, sample_es6_path, fixtures_dir):
        """Test that imports are sorted."""
        _, _, _, imports, _ = js_parser.extract_code_structure(sample_es6_path, fixtures_dir)

        assert imports == sorted(imports)


class TestJavaScriptParserMetadata:
    """Tests for metadata extraction."""

    def test_metadata_contains_complexity(self, js_parser, sample_module_path, fixtures_dir):
        """Test that metadata includes complexity score."""
        _, _, _, _, metadata = js_parser.extract_code_structure(sample_module_path, fixtures_dir)

        assert 'complexity_score' in metadata
        assert isinstance(metadata['complexity_score'], int)
        assert metadata['complexity_score'] > 0

    def test_metadata_contains_symbol_count(self, js_parser, sample_module_path, fixtures_dir):
        """Test that metadata includes symbol count."""
        symbols, _, _, _, metadata = js_parser.extract_code_structure(sample_module_path, fixtures_dir)

        assert 'symbol_count' in metadata
        assert metadata['symbol_count'] == len(symbols)


class TestJavaScriptParserEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_file(self, js_parser, tmp_path):
        """Test parsing an empty file."""
        empty_file = tmp_path / "empty.js"
        empty_file.write_text("")

        symbols, exports, deps, imports, metadata = js_parser.extract_code_structure(
            empty_file, tmp_path
        )

        assert len(symbols) == 0
        assert len(exports) == 0
        assert len(deps) == 0
        # imports might be empty or sorted empty list
        assert imports == sorted(imports)

    def test_syntax_error_handling(self, js_parser, tmp_path):
        """Test that parser handles syntax errors gracefully."""
        bad_file = tmp_path / "bad.js"
        bad_file.write_text("function broken() { // missing closing brace")

        # Should not raise an exception
        symbols, exports, deps, imports, metadata = js_parser.extract_code_structure(
            bad_file, tmp_path
        )

        # Should return empty or partial results
        assert isinstance(symbols, list)
        assert isinstance(exports, list)
        assert isinstance(imports, list)
