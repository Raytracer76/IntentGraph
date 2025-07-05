"""Property-based testing for parser robustness."""

import ast
import string
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, strategies as st, assume

from src.intentgraph.adapters.parsers.enhanced_python_parser import EnhancedPythonParser


class TestPropertyBasedParsers:
    """Property-based tests for parser robustness."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EnhancedPythonParser()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @given(st.text(alphabet=string.ascii_letters + string.digits + "_", min_size=1, max_size=50))
    def test_python_parser_robustness(self, function_name):
        """Test parser robustness with generated function names."""
        assume(function_name.isidentifier())
        assume(not function_name.startswith("__"))
        
        # Generate valid Python code with random function name
        test_code = f'''
def {function_name}():
    """Generated function."""
    return "test"

class Test{function_name.title()}:
    """Generated class."""
    pass
'''
        
        test_file = self.temp_dir / "generated.py"
        test_file.write_text(test_code)
        
        # Parser should not crash
        try:
            symbols, exports, deps, imports, metadata = self.parser.extract_code_structure(
                test_file, self.temp_dir
            )
            
            # Should extract expected symbols
            symbol_names = [s.name for s in symbols]
            assert function_name in symbol_names
            assert f"Test{function_name.title()}" in symbol_names
            
        except Exception as e:
            # If it fails, it should be due to invalid Python syntax only
            pytest.fail(f"Parser crashed on valid input '{function_name}': {e}")

    @given(st.lists(st.text(alphabet=string.ascii_letters + "._", min_size=1, max_size=20), 
                   min_size=1, max_size=10))
    def test_import_resolution_robustness(self, import_paths):
        """Test import resolution with various paths."""
        # Filter to valid module names
        valid_imports = []
        for path in import_paths:
            if all(part.isidentifier() for part in path.split('.') if part):
                valid_imports.append(path)
        
        assume(len(valid_imports) > 0)
        
        # Generate import statements
        import_statements = []
        for imp in valid_imports[:5]:  # Limit to prevent excessive generation
            import_statements.append(f"import {imp}")
        
        test_code = '\n'.join(import_statements) + '\n\ndef test_function():\n    pass'
        
        test_file = self.temp_dir / "imports.py"
        test_file.write_text(test_code)
        
        # Should handle imports gracefully
        try:
            symbols, exports, deps, imports, metadata = self.parser.extract_code_structure(
                test_file, self.temp_dir
            )
            
            # Should extract imports
            assert len(imports) >= len(valid_imports)
            
        except Exception as e:
            pytest.fail(f"Parser failed on import resolution: {e}")

    @given(st.integers(min_value=1, max_value=20))
    def test_complexity_calculation_robustness(self, complexity_depth):
        """Test complexity calculation with nested structures."""
        # Generate nested if statements
        indent = "    "
        nested_ifs = ""
        for i in range(complexity_depth):
            nested_ifs += f"{indent * (i + 1)}if x > {i}:\n"
            nested_ifs += f"{indent * (i + 2)}y = {i}\n"
        
        test_code = f'''
def complex_function(x):
    """Function with nested complexity."""
    y = 0
{nested_ifs}
    return y
'''
        
        test_file = self.temp_dir / "complex.py"
        test_file.write_text(test_code)
        
        # Should calculate complexity without crashing
        try:
            symbols, exports, deps, imports, metadata = self.parser.extract_code_structure(
                test_file, self.temp_dir
            )
            
            # Complexity should be reasonable
            assert metadata.get("complexity_score", 0) >= complexity_depth
            assert metadata.get("complexity_score", 0) <= complexity_depth * 2
            
        except Exception as e:
            pytest.fail(f"Complexity calculation failed: {e}")

    @given(st.text(min_size=0, max_size=1000))
    def test_malformed_input_handling(self, random_text):
        """Test handling of potentially malformed input."""
        test_file = self.temp_dir / "malformed.py"
        test_file.write_text(random_text)
        
        # Should not crash, even on invalid input
        try:
            symbols, exports, deps, imports, metadata = self.parser.extract_code_structure(
                test_file, self.temp_dir
            )
            
            # Should return empty results for invalid syntax
            # (or valid results if the random text happens to be valid Python)
            assert isinstance(symbols, list)
            assert isinstance(exports, list)
            assert isinstance(deps, list)
            assert isinstance(imports, list)
            assert isinstance(metadata, dict)
            
        except Exception as e:
            # Should only fail on file I/O errors, not parsing errors
            assert "encoding" in str(e).lower() or "permission" in str(e).lower()

    @given(st.lists(st.text(alphabet=string.ascii_letters + "_", min_size=1, max_size=20),
                   min_size=1, max_size=10))
    def test_symbol_extraction_robustness(self, symbol_names):
        """Test symbol extraction with various symbol names."""
        # Filter to valid identifiers
        valid_names = [name for name in symbol_names if name.isidentifier()]
        assume(len(valid_names) >= 2)
        
        # Generate code with multiple symbols
        functions = [f"def {name}(): pass" for name in valid_names[:3]]
        classes = [f"class {name.title()}: pass" for name in valid_names[3:6]]
        variables = [f"{name.upper()} = {i}" for i, name in enumerate(valid_names[6:9])]
        
        test_code = '\n'.join(functions + classes + variables)
        
        test_file = self.temp_dir / "symbols.py"
        test_file.write_text(test_code)
        
        # Should extract all symbols
        try:
            symbols, exports, deps, imports, metadata = self.parser.extract_code_structure(
                test_file, self.temp_dir
            )
            
            symbol_names_found = [s.name for s in symbols]
            
            # Should find most generated symbols
            found_count = sum(1 for name in valid_names[:9] 
                            if name in symbol_names_found or name.title() in symbol_names_found or name.upper() in symbol_names_found)
            assert found_count >= min(len(valid_names), 3)
            
        except Exception as e:
            pytest.fail(f"Symbol extraction failed: {e}")

    @given(st.integers(min_value=1, max_value=100))
    def test_file_size_scalability(self, line_count):
        """Test parser scalability with varying file sizes."""
        # Generate file with specified number of lines
        lines = []
        for i in range(line_count):
            if i % 10 == 0:
                lines.append(f"def function_{i}():")
                lines.append(f"    \"\"\"Function {i}.\"\"\"")
                lines.append(f"    return {i}")
            elif i % 7 == 0:
                lines.append(f"class Class{i}:")
                lines.append(f"    \"\"\"Class {i}.\"\"\"")
                lines.append("    pass")
            else:
                lines.append(f"# Comment line {i}")
        
        test_code = '\n'.join(lines)
        test_file = self.temp_dir / "large.py"
        test_file.write_text(test_code)
        
        # Should handle files of various sizes
        try:
            symbols, exports, deps, imports, metadata = self.parser.extract_code_structure(
                test_file, self.temp_dir
            )
            
            # Should extract reasonable number of symbols
            expected_functions = line_count // 10
            expected_classes = line_count // 7
            
            function_count = len([s for s in symbols if s.symbol_type == "function"])
            class_count = len([s for s in symbols if s.symbol_type == "class"])
            
            # Allow some tolerance for overlap
            assert function_count >= expected_functions * 0.8
            assert class_count >= expected_classes * 0.5
            
        except Exception as e:
            pytest.fail(f"Parser failed on file with {line_count} lines: {e}")

    def test_ast_error_recovery(self):
        """Test AST error recovery mechanisms."""
        # Test various syntax errors
        syntax_errors = [
            "def function(:\n    pass",  # Missing parameter
            "class Class\n    pass",     # Missing colon
            "if True\n    x = 1",       # Missing colon
            "def func():\nreturn 1",     # Missing indentation
            "import",                    # Incomplete import
            "from import x",             # Invalid from import
        ]
        
        for i, error_code in enumerate(syntax_errors):
            test_file = self.temp_dir / f"error_{i}.py"
            test_file.write_text(error_code)
            
            # Should handle syntax errors gracefully
            symbols, exports, deps, imports, metadata = self.parser.extract_code_structure(
                test_file, self.temp_dir
            )
            
            # Should return empty results for invalid syntax
            assert symbols == []
            assert exports == []
            assert deps == []
            assert imports == []
            assert metadata == {}

    @given(st.text(alphabet='"\'\\n\\t ', min_size=0, max_size=100))
    def test_string_content_robustness(self, string_content):
        """Test robustness with various string contents."""
        # Escape the string content for Python syntax
        escaped_content = repr(string_content)
        
        test_code = f'''
def test_function():
    """Test function with string."""
    content = {escaped_content}
    return content

STRING_CONSTANT = {escaped_content}
'''
        
        test_file = self.temp_dir / "strings.py"
        test_file.write_text(test_code)
        
        # Should handle various string contents
        try:
            symbols, exports, deps, imports, metadata = self.parser.extract_code_structure(
                test_file, self.temp_dir
            )
            
            # Should extract symbols regardless of string content
            symbol_names = [s.name for s in symbols]
            assert "test_function" in symbol_names
            assert "STRING_CONSTANT" in symbol_names
            
        except Exception as e:
            pytest.fail(f"Parser failed on string content: {e}")