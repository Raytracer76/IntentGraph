"""Comprehensive tests for EnhancedPythonParser."""

import ast
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from intentgraph.adapters.parsers.enhanced_python_parser import (
    EnhancedPythonParser, 
    ASTDataCollector
)
from intentgraph.domain.models import CodeSymbol


class TestEnhancedPythonParser:
    """Test suite for EnhancedPythonParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EnhancedPythonParser()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_extract_code_structure_basic(self):
        """Test basic code structure extraction."""
        test_code = '''
def hello_world():
    """Say hello to the world."""
    return "Hello, world!"

class TestClass:
    """A test class."""
    
    def method(self):
        return self.hello_world()

CONSTANT = "test"
variable = 42
'''
        test_file = self.temp_dir / "test.py"
        test_file.write_text(test_code)
        
        symbols, exports, func_deps, imports, metadata = self.parser.extract_code_structure(
            test_file, self.temp_dir
        )
        
        # Check symbols
        assert len(symbols) >= 4  # function, class, method, constant, variable
        symbol_names = [s.name for s in symbols]
        assert "hello_world" in symbol_names
        assert "TestClass" in symbol_names
        assert "CONSTANT" in symbol_names
        assert "variable" in symbol_names
        
        # Check exports
        assert len(exports) > 0
        export_names = [e.name for e in exports]
        assert "hello_world" in export_names
        assert "TestClass" in export_names
        
        # Check metadata
        assert "complexity_score" in metadata
        assert "maintainability_index" in metadata
        assert metadata["complexity_score"] > 0

    def test_extract_symbols_functions(self):
        """Test function symbol extraction."""
        test_code = '''
def simple_function():
    pass

async def async_function(param: str) -> str:
    """An async function with annotations."""
    return param

@decorator
def decorated_function():
    pass

def _private_function():
    pass
'''
        test_file = self.temp_dir / "functions.py"
        test_file.write_text(test_code)
        
        symbols, _, _, _, _ = self.parser.extract_code_structure(test_file, self.temp_dir)
        
        function_symbols = [s for s in symbols if s.symbol_type in ("function", "async_function")]
        assert len(function_symbols) == 4
        
        # Check async function
        async_func = next(s for s in function_symbols if s.name == "async_function")
        assert async_func.symbol_type == "async_function"
        assert "async def" in async_func.signature
        assert async_func.docstring == "An async function with annotations."
        assert async_func.is_exported
        
        # Check private function
        private_func = next(s for s in function_symbols if s.name == "_private_function")
        assert private_func.is_private
        assert not private_func.is_exported
        
        # Check decorated function
        decorated_func = next(s for s in function_symbols if s.name == "decorated_function")
        assert "decorator" in decorated_func.decorators

    def test_extract_symbols_classes(self):
        """Test class symbol extraction."""
        test_code = '''
class SimpleClass:
    """A simple class."""
    pass

class InheritedClass(SimpleClass):
    pass

@dataclass
class DecoratedClass:
    name: str

class _PrivateClass:
    pass
'''
        test_file = self.temp_dir / "classes.py"
        test_file.write_text(test_code)
        
        symbols, _, _, _, _ = self.parser.extract_code_structure(test_file, self.temp_dir)
        
        class_symbols = [s for s in symbols if s.symbol_type == "class"]
        assert len(class_symbols) == 4
        
        # Check inheritance
        inherited_class = next(s for s in class_symbols if s.name == "InheritedClass")
        assert "SimpleClass" in inherited_class.signature
        
        # Check decorated class
        decorated_class = next(s for s in class_symbols if s.name == "DecoratedClass")
        assert "dataclass" in decorated_class.decorators
        
        # Check private class
        private_class = next(s for s in class_symbols if s.name == "_PrivateClass")
        assert private_class.is_private
        assert not private_class.is_exported

    def test_calculate_cyclomatic_complexity(self):
        """Test complexity calculation."""
        test_code = '''
def complex_function(x):
    if x > 0:
        if x > 10:
            return "high"
        else:
            return "medium"
    elif x < 0:
        return "negative"
    else:
        return "zero"
        
    while x > 0:
        x -= 1
        
    for i in range(x):
        if i % 2 == 0:
            continue
'''
        test_file = self.temp_dir / "complex.py"
        test_file.write_text(test_code)
        
        symbols, _, _, _, metadata = self.parser.extract_code_structure(test_file, self.temp_dir)
        
        # Should have high complexity due to multiple decision points
        assert metadata["complexity_score"] > 5

    def test_error_handling_malformed_syntax(self):
        """Test handling of syntax errors."""
        test_code = '''
def malformed_function(:
    pass
    
invalid syntax here :::
'''
        test_file = self.temp_dir / "malformed.py"
        test_file.write_text(test_code)
        
        # Should not raise exception, but return empty results
        symbols, exports, func_deps, imports, metadata = self.parser.extract_code_structure(
            test_file, self.temp_dir
        )
        
        assert symbols == []
        assert exports == []
        assert func_deps == []
        assert imports == []
        assert metadata == {}

    def test_extract_imports(self):
        """Test import extraction."""
        test_code = '''
import os
import sys
from pathlib import Path
from typing import Dict, List
from ..relative import module
'''
        test_file = self.temp_dir / "imports.py"
        test_file.write_text(test_code)
        
        symbols, _, _, imports, _ = self.parser.extract_code_structure(test_file, self.temp_dir)
        
        assert "import os" in imports
        assert "import sys" in imports
        assert "from pathlib import Path" in imports
        assert "from typing import Dict, List" in imports
        assert "from ..relative import module" in imports

    def test_extract_api_exports_with_all(self):
        """Test API export extraction with __all__ defined."""
        test_code = '''
__all__ = ["public_function", "PublicClass"]

def public_function():
    pass

def private_function():
    pass

class PublicClass:
    pass

class PrivateClass:
    pass
'''
        test_file = self.temp_dir / "exports.py"
        test_file.write_text(test_code)
        
        symbols, exports, _, _, _ = self.parser.extract_code_structure(test_file, self.temp_dir)
        
        export_names = [e.name for e in exports]
        assert "public_function" in export_names
        assert "PublicClass" in export_names
        assert "private_function" not in export_names
        assert "PrivateClass" not in export_names

    def test_file_dependencies_extraction(self):
        """Test file-level dependency extraction."""
        test_file = self.temp_dir / "dependent.py"
        test_file.write_text("import os\nfrom pathlib import Path")
        
        dependencies = self.parser.extract_dependencies(test_file, self.temp_dir)
        
        # Should return list of dependency paths
        assert isinstance(dependencies, list)

    def test_single_pass_efficiency(self):
        """Test that single-pass traversal works correctly."""
        test_code = '''
import os

class TestClass:
    def method(self):
        if True:
            return os.path.join("a", "b")

def function():
    while True:
        break

CONSTANT = 42
'''
        test_file = self.temp_dir / "efficiency.py"
        test_file.write_text(test_code)
        
        # Use collector directly to verify single-pass operation
        tree = ast.parse(test_code)
        collector = ASTDataCollector()
        collector.visit(tree)
        
        # Verify all data was collected in single pass
        assert len(collector.symbols) == 4  # class, method, function, constant
        assert len(collector.imports) == 1
        assert collector.complexity_nodes > 0
        assert collector.function_count == 2
        assert collector.class_count == 1


class TestASTDataCollector:
    """Test suite for ASTDataCollector."""

    def test_visit_function_def(self):
        """Test function definition visitor."""
        code = "def test_func(): pass"
        tree = ast.parse(code)
        
        collector = ASTDataCollector()
        collector.visit(tree)
        
        assert collector.function_count == 1
        assert len(collector.symbols) == 1
        assert collector.symbols[0]['name'] == 'test_func'
        assert collector.symbols[0]['type'] == 'function'

    def test_visit_async_function_def(self):
        """Test async function definition visitor."""
        code = "async def async_func(): pass"
        tree = ast.parse(code)
        
        collector = ASTDataCollector()
        collector.visit(tree)
        
        assert collector.function_count == 1
        assert collector.symbols[0]['is_async'] is True

    def test_visit_class_def(self):
        """Test class definition visitor."""
        code = "class TestClass: pass"
        tree = ast.parse(code)
        
        collector = ASTDataCollector()
        collector.visit(tree)
        
        assert collector.class_count == 1
        assert len(collector.symbols) == 1
        assert collector.symbols[0]['name'] == 'TestClass'
        assert collector.symbols[0]['type'] == 'class'

    def test_visit_assign_all_exports(self):
        """Test __all__ assignment visitor."""
        code = '__all__ = ["func1", "func2"]'
        tree = ast.parse(code)
        
        collector = ASTDataCollector()
        collector.visit(tree)
        
        assert collector.all_exports == ["func1", "func2"]

    def test_complexity_tracking(self):
        """Test complexity node tracking."""
        code = '''
if True:
    while False:
        for i in range(10):
            try:
                with open("file"):
                    pass
            except:
                pass
'''
        tree = ast.parse(code)
        
        collector = ASTDataCollector()
        collector.visit(tree)
        
        # Should track if, while, for, try/except, with statements
        assert collector.complexity_nodes >= 5

    def test_create_symbols(self):
        """Test symbol creation from collected data."""
        code = '''
def test_func():
    """Test function."""
    pass

class TestClass:
    """Test class."""
    pass

CONSTANT = 42
'''
        tree = ast.parse(code)
        
        collector = ASTDataCollector()
        collector.visit(tree)
        
        symbols = collector.create_symbols(code.splitlines())
        
        assert len(symbols) == 3
        symbol_names = [s.name for s in symbols]
        assert "test_func" in symbol_names
        assert "TestClass" in symbol_names
        assert "CONSTANT" in symbol_names
        
        # Check symbol types
        func_symbol = next(s for s in symbols if s.name == "test_func")
        assert func_symbol.symbol_type == "function"
        assert func_symbol.docstring == "Test function."
        
        class_symbol = next(s for s in symbols if s.name == "TestClass")
        assert class_symbol.symbol_type == "class"
        
        const_symbol = next(s for s in symbols if s.name == "CONSTANT")
        assert const_symbol.symbol_type == "constant"


@pytest.mark.integration
class TestEnhancedPythonParserIntegration:
    """Integration tests for EnhancedPythonParser."""

    def test_real_python_file_analysis(self):
        """Test analysis of a real Python file."""
        parser = EnhancedPythonParser()
        
        # Use the parser file itself as test subject
        parser_file = Path("src/intentgraph/adapters/parsers/enhanced_python_parser.py")
        repo_path = Path(".")
        
        if parser_file.exists():
            symbols, exports, func_deps, imports, metadata = parser.extract_code_structure(
                parser_file, repo_path
            )
            
            # Should find the EnhancedPythonParser class
            class_names = [s.name for s in symbols if s.symbol_type == "class"]
            assert "EnhancedPythonParser" in class_names
            assert "ASTDataCollector" in class_names
            
            # Should have imports
            assert len(imports) > 0
            
            # Should have positive complexity
            assert metadata["complexity_score"] > 0
            assert metadata["total_functions"] > 0
            assert metadata["total_classes"] > 0

    def test_parser_performance(self):
        """Test parser performance with moderately sized file."""
        import time
        
        # Create a moderately complex test file
        test_code = """
import os
import sys
from pathlib import Path

class BaseClass:
    def __init__(self):
        self.value = 0
    
    def method1(self):
        if self.value > 0:
            return True
        return False

class DerivedClass(BaseClass):
    def __init__(self):
        super().__init__()
        self.data = []
    
    def complex_method(self, param):
        for i in range(100):
            if i % 2 == 0:
                self.data.append(i)
            elif i % 3 == 0:
                self.data.append(i * 2)
            else:
                continue
        
        try:
            with open("test.txt") as f:
                content = f.read()
        except FileNotFoundError:
            content = ""
        
        return content

def utility_function(a, b, c=None):
    if c is None:
        c = a + b
    
    while c > 0:
        c -= 1
        
    return c

CONSTANT1 = "test"
CONSTANT2 = 42
variable = [1, 2, 3, 4, 5]
"""
        
        temp_dir = Path(tempfile.mkdtemp())
        test_file = temp_dir / "complex_test.py"
        test_file.write_text(test_code)
        
        parser = EnhancedPythonParser()
        
        start_time = time.time()
        symbols, exports, func_deps, imports, metadata = parser.extract_code_structure(
            test_file, temp_dir
        )
        end_time = time.time()
        
        # Should complete quickly (under 1 second for this size)
        assert end_time - start_time < 1.0
        
        # Should extract all expected elements
        assert len(symbols) >= 7  # 2 classes, 3+ methods, 2 functions, 3 variables
        assert len(imports) == 3
        assert metadata["complexity_score"] > 10  # Should have reasonable complexity
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)