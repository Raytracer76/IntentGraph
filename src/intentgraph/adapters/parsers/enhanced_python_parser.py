"""Enhanced Python parser with detailed code structure analysis."""

import ast
import logging
from pathlib import Path
from typing import Optional, Any
from uuid import uuid4

from .base import LanguageParser
from ...domain.models import CodeSymbol, APIExport, FunctionDependency

logger = logging.getLogger(__name__)


class EnhancedPythonParser(LanguageParser):
    """Enhanced Python parser that extracts detailed code structure."""

    def __init__(self):
        self._symbol_map = {}  # Maps symbol names to UUIDs for dependency tracking
        
    def extract_dependencies(self, file_path: Path, repo_path: Path) -> list[str]:
        """Extract file-level dependencies (existing functionality)."""
        # Use existing logic from python_parser.py
        return self._extract_file_dependencies(file_path, repo_path)
        
    def extract_code_structure(self, file_path: Path, repo_path: Path) -> tuple[
        list[CodeSymbol], 
        list[APIExport], 
        list[FunctionDependency],
        list[str],  # imports
        dict[str, Any]  # metadata
    ]:
        """Extract detailed code structure from Python file."""
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            symbols = []
            exports = []
            function_deps = []
            imports = []
            self._symbol_map = {}  # Reset for this file
            
            # First pass: Extract all symbols
            symbols = self._extract_symbols(tree, content)
            
            # Second pass: Extract imports
            imports = self._extract_imports(tree)
            
            # Third pass: Extract function-level dependencies
            function_deps = self._extract_function_dependencies(tree, file_path, repo_path)
            
            # Fourth pass: Determine API exports
            exports = self._extract_api_exports(tree, symbols, file_path)
            
            # Calculate metadata
            metadata = self._calculate_metadata(tree, content)
            
            return symbols, exports, function_deps, imports, metadata
            
        except Exception as e:
            logger.warning(f"Failed to parse code structure for {file_path}: {e}")
            return [], [], [], [], {}
    
    def _extract_symbols(self, tree: ast.AST, content: str) -> list[CodeSymbol]:
        """Extract all code symbols (functions, classes, variables)."""
        symbols = []
        lines = content.splitlines()
        
        for node in ast.walk(tree):
            symbol = None
            
            if isinstance(node, ast.FunctionDef):
                symbol = self._create_function_symbol(node, lines)
            elif isinstance(node, ast.AsyncFunctionDef):
                symbol = self._create_function_symbol(node, lines, is_async=True)
            elif isinstance(node, ast.ClassDef):
                symbol = self._create_class_symbol(node, lines)
            elif isinstance(node, ast.Assign):
                # Module-level variables
                if self._is_module_level(node):
                    symbol = self._create_variable_symbol(node, lines)
                    
            if symbol:
                symbols.append(symbol)
                self._symbol_map[symbol.name] = symbol.id
                
        return symbols
    
    def _create_function_symbol(self, node: ast.FunctionDef, lines: list[str], is_async: bool = False) -> CodeSymbol:
        """Create a CodeSymbol for a function."""
        
        # Extract signature
        signature = self._get_function_signature(node, is_async)
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Check if exported (not starting with _)
        is_exported = not node.name.startswith('_')
        is_private = node.name.startswith('_')
        
        # Extract decorators
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        
        # Determine parent (for nested functions)
        parent = self._find_parent_symbol(node)
        
        return CodeSymbol(
            name=node.name,
            symbol_type="async_function" if is_async else "function",
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            signature=signature,
            docstring=docstring,
            is_exported=is_exported,
            is_private=is_private,
            decorators=decorators,
            parent=parent
        )
    
    def _create_class_symbol(self, node: ast.ClassDef, lines: list[str]) -> CodeSymbol:
        """Create a CodeSymbol for a class."""
        
        # Extract class signature with inheritance
        bases = [self._get_node_name(base) for base in node.bases]
        signature = f"class {node.name}"
        if bases:
            signature += f"({', '.join(bases)})"
            
        docstring = ast.get_docstring(node)
        is_exported = not node.name.startswith('_')
        is_private = node.name.startswith('_')
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        
        return CodeSymbol(
            name=node.name,
            symbol_type="class",
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            signature=signature,
            docstring=docstring,
            is_exported=is_exported,
            is_private=is_private,
            decorators=decorators
        )
    
    def _create_variable_symbol(self, node: ast.Assign, lines: list[str]) -> Optional[CodeSymbol]:
        """Create a CodeSymbol for a module-level variable."""
        
        # Only handle simple assignments for now
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            
            # Try to determine if it's a constant (ALL_CAPS)
            symbol_type = "constant" if var_name.isupper() else "variable"
            
            is_exported = not var_name.startswith('_')
            is_private = var_name.startswith('_')
            
            return CodeSymbol(
                name=var_name,
                symbol_type=symbol_type,
                line_start=node.lineno,
                line_end=node.end_lineno or node.lineno,
                signature=f"{var_name} = ...",
                is_exported=is_exported,
                is_private=is_private
            )
        return None
    
    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """Extract all import statements."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    level = '.' * node.level if node.level else ''
                    names = ', '.join(alias.name for alias in node.names)
                    imports.append(f"from {level}{node.module} import {names}")
                    
        return imports
    
    def _extract_function_dependencies(self, tree: ast.AST, file_path: Path, repo_path: Path) -> list[FunctionDependency]:
        """Extract function-level dependencies."""
        dependencies = []
        
        # This is a simplified implementation
        # In practice, you'd want more sophisticated analysis
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Function calls
                if isinstance(node.func, ast.Name):
                    caller = self._find_containing_function(node)
                    if caller and node.func.id in self._symbol_map:
                        dep = FunctionDependency(
                            from_symbol=self._symbol_map[caller],
                            to_symbol=self._symbol_map[node.func.id],
                            to_file=uuid4(),  # Would need to resolve this properly
                            dependency_type="calls",
                            line_number=node.lineno
                        )
                        dependencies.append(dep)
                        
        return dependencies
    
    def _extract_api_exports(self, tree: ast.AST, symbols: list[CodeSymbol], file_path: Path) -> list[APIExport]:
        """Determine what this module exports."""
        exports = []
        
        # Check for __all__ definition
        all_exports = self._find_all_exports(tree)
        
        if all_exports:
            # Use explicit __all__ list
            for name in all_exports:
                symbol = next((s for s in symbols if s.name == name), None)
                export = APIExport(
                    name=name,
                    export_type=symbol.symbol_type if symbol else "unknown",
                    symbol_id=symbol.id if symbol else None
                )
                exports.append(export)
        else:
            # Export all public symbols (not starting with _)
            for symbol in symbols:
                if symbol.is_exported:
                    export = APIExport(
                        name=symbol.name,
                        export_type=symbol.symbol_type,
                        symbol_id=symbol.id,
                        docstring=symbol.docstring
                    )
                    exports.append(export)
                    
        return exports
    
    def _calculate_metadata(self, tree: ast.AST, content: str) -> dict[str, Any]:
        """Calculate various code metrics."""
        
        # Simple complexity calculation (count decision points)
        complexity = self._calculate_cyclomatic_complexity(tree)
        
        # Maintainability index (simplified)
        loc = len([line for line in content.splitlines() if line.strip()])
        maintainability = max(0, 171 - 5.2 * complexity - 0.23 * loc)
        
        return {
            "complexity_score": complexity,
            "maintainability_index": maintainability,
            "total_functions": len([n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]),
            "total_classes": len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
        }
    
    # Helper methods
    def _get_function_signature(self, node: ast.FunctionDef, is_async: bool = False) -> str:
        """Extract function signature as string."""
        prefix = "async def" if is_async else "def"
        args = self._format_arguments(node.args)
        return_annotation = ""
        if node.returns:
            return_annotation = f" -> {ast.unparse(node.returns)}"
        return f"{prefix} {node.name}({args}){return_annotation}"
    
    def _format_arguments(self, args: ast.arguments) -> str:
        """Format function arguments."""
        # Simplified - would need more robust implementation
        arg_strs = []
        for arg in args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            arg_strs.append(arg_str)
        return ", ".join(arg_strs)
    
    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Get decorator name as string."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
            return decorator.func.id
        else:
            return ast.unparse(decorator)
    
    def _get_node_name(self, node: ast.expr) -> str:
        """Get name from various node types."""
        if isinstance(node, ast.Name):
            return node.id
        else:
            return ast.unparse(node)
    
    def _find_parent_symbol(self, node: ast.AST) -> Optional[str]:
        """Find parent symbol for nested definitions."""
        # Would need to traverse up the AST to find containing class/function
        return None
    
    def _is_module_level(self, node: ast.AST) -> bool:
        """Check if node is at module level."""
        # Simplified check - would need proper AST traversal
        return True
    
    def _find_containing_function(self, node: ast.AST) -> Optional[str]:
        """Find the function that contains this node."""
        # Would need to traverse up the AST
        return None
    
    def _find_all_exports(self, tree: ast.AST) -> list[str]:
        """Find __all__ exports if defined."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            return [elt.s for elt in node.value.elts if isinstance(elt, ast.Str)]
        return []
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, 
                               ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
                
        return complexity
    
    def _extract_file_dependencies(self, file_path: Path, repo_path: Path) -> list[str]:
        """Extract file-level dependencies (fallback to existing logic)."""
        # For now, use simple AST-based approach
        # This should be integrated with the existing grimp-based logic
        dependencies = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name:
                            deps = self._resolve_import_path(alias.name, file_path, repo_path)
                            dependencies.extend(deps)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        deps = self._resolve_import_path(node.module, file_path, repo_path)
                        dependencies.extend(deps)
                        
        except Exception as e:
            logger.warning(f"Failed to extract dependencies for {file_path}: {e}")
            
        return dependencies
    
    def _get_file_extensions(self) -> list[str]:
        """Get Python file extensions."""
        return ['.py']

    def _get_init_files(self) -> list[str]:
        """Get Python initialization files."""
        return ['__init__.py']