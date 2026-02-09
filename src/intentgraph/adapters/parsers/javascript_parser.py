"""JavaScript dependency parser using tree-sitter with deterministic analysis."""

import hashlib
import logging
from pathlib import Path
from typing import Optional, Any
from uuid import UUID

from tree_sitter_language_pack import get_language, get_parser

from .base import LanguageParser
from ...domain.models import CodeSymbol, APIExport, FunctionDependency

logger = logging.getLogger(__name__)


class JavaScriptParser(LanguageParser):
    """Parser for JavaScript files using tree-sitter with enhanced structure extraction."""

    _language = None
    _parser = None

    @classmethod
    def _get_language(cls):
        """Lazy initialization of tree-sitter language."""
        if cls._language is None:
            cls._language = get_language('javascript')
        return cls._language

    @classmethod
    def _get_parser(cls):
        """Lazy initialization of tree-sitter parser."""
        if cls._parser is None:
            cls._parser = get_parser('javascript')
        return cls._parser

    def extract_dependencies(self, file_path: Path, repo_path: Path) -> list[str]:
        """Extract JavaScript dependencies using tree-sitter."""
        dependencies = []

        try:
            content = file_path.read_bytes()
            parser = self._get_parser()
            language = self._get_language()
            tree = parser.parse(content)

            # Query for import statements
            query = language.query("""
                (import_statement source: (string) @import)
                (call_expression
                    function: (identifier) @func
                    arguments: (arguments (string) @require)
                    (#eq? @func "require"))
            """)

            captures = query.captures(tree.root_node)

            for node, capture_name in captures:
                if capture_name in ['import', 'require']:
                    import_path = node.text.decode('utf-8').strip('"\'')

                    # Skip external modules (not starting with . or /)
                    if not import_path.startswith('.') and not import_path.startswith('/'):
                        continue

                    deps = self._resolve_import_path(import_path, file_path, repo_path)
                    dependencies.extend(deps)

        except Exception as e:
            logger.warning(f"Failed to parse JavaScript file {file_path}: {e}")

        # Sort for determinism
        return sorted(list(set(dependencies)))

    def extract_code_structure(self, file_path: Path, repo_path: Path) -> tuple[
        list[CodeSymbol],
        list[APIExport],
        list[FunctionDependency],
        list[str],  # imports
        dict[str, Any]  # metadata
    ]:
        """Extract detailed code structure from JavaScript file."""
        symbols = []
        exports = []
        function_deps = []
        imports = []
        metadata = {}

        try:
            content = file_path.read_bytes()
            text = content.decode('utf-8')
            lines = text.splitlines()

            parser = self._get_parser()
            language = self._get_language()
            tree = parser.parse(content)
            root = tree.root_node

            # Extract imports (both require and ES6)
            imports = self._extract_imports(root, text)

            # Extract symbols (functions and classes)
            symbols = self._extract_symbols(root, text, lines, file_path, repo_path)

            # Extract exports
            exports = self._extract_exports(root, text, symbols)

            # Calculate metadata
            metadata = self._calculate_metadata(root, text, len(symbols))

        except Exception as e:
            logger.warning(f"Failed to extract structure from {file_path}: {e}")

        # Sort for determinism
        symbols.sort(key=lambda s: (s.line_start, s.symbol_type, s.name))
        exports.sort(key=lambda e: e.name)
        imports.sort()

        return symbols, exports, function_deps, imports, metadata

    def _extract_imports(self, root_node, text: str) -> list[str]:
        """Extract import statements from JavaScript code."""
        imports = []
        language = self._get_language()

        # Query for ES6 imports and CommonJS requires
        query = language.query("""
            (import_statement source: (string) @import_source)
            (call_expression
                function: (identifier) @func
                arguments: (arguments (string) @require_source)
                (#eq? @func "require"))
        """)

        captures = query.captures(root_node)

        for node, capture_name in captures:
            if capture_name in ['import_source', 'require_source']:
                import_path = node.text.decode('utf-8').strip('"\'')
                if capture_name == 'require_source':
                    imports.append(f"require('{import_path}')")
                else:
                    imports.append(f"import ... from '{import_path}'")

        return imports

    def _extract_symbols(self, root_node, text: str, lines: list[str],
                        file_path: Path, repo_path: Path) -> list[CodeSymbol]:
        """Extract function and class symbols from JavaScript code."""
        symbols = []
        language = self._get_language()

        # Query for functions and classes
        query = language.query("""
            (function_declaration name: (identifier) @func_name) @function
            (arrow_function) @arrow
            (class_declaration name: (identifier) @class_name) @class
            (method_definition name: (property_identifier) @method_name) @method
            (variable_declarator
                name: (identifier) @var_name
                value: [(function_expression) (arrow_function)] @var_func)
        """)

        captures = query.captures(root_node)

        # Group captures by type
        i = 0
        while i < len(captures):
            node, capture_name = captures[i]

            if capture_name == 'function':
                # Regular function declaration
                func_name_node = None
                for j in range(i, min(i + 5, len(captures))):
                    if captures[j][1] == 'func_name':
                        func_name_node = captures[j][0]
                        break

                if func_name_node:
                    name = func_name_node.text.decode('utf-8')
                    symbol = self._create_symbol(
                        name=name,
                        symbol_type='function',
                        node=node,
                        lines=lines,
                        file_path=file_path,
                        repo_path=repo_path
                    )
                    symbols.append(symbol)

            elif capture_name == 'class':
                # Class declaration
                class_name_node = None
                for j in range(i, min(i + 5, len(captures))):
                    if captures[j][1] == 'class_name':
                        class_name_node = captures[j][0]
                        break

                if class_name_node:
                    name = class_name_node.text.decode('utf-8')
                    symbol = self._create_symbol(
                        name=name,
                        symbol_type='class',
                        node=node,
                        lines=lines,
                        file_path=file_path,
                        repo_path=repo_path
                    )
                    symbols.append(symbol)

            elif capture_name == 'var_func':
                # Variable with function/arrow function value
                var_name_node = None
                for j in range(max(0, i - 3), i):
                    if captures[j][1] == 'var_name':
                        var_name_node = captures[j][0]
                        break

                if var_name_node:
                    name = var_name_node.text.decode('utf-8')
                    symbol = self._create_symbol(
                        name=name,
                        symbol_type='function',
                        node=node,
                        lines=lines,
                        file_path=file_path,
                        repo_path=repo_path
                    )
                    symbols.append(symbol)

            i += 1

        return symbols

    def _create_symbol(self, name: str, symbol_type: str, node, lines: list[str],
                      file_path: Path, repo_path: Path) -> CodeSymbol:
        """Create a CodeSymbol with deterministic ID."""
        line_start = node.start_point[0] + 1
        line_end = node.end_point[0] + 1

        # Generate deterministic ID using canonical path + kind + name + span
        canonical_path = str(file_path.relative_to(repo_path))
        span_str = f"{line_start}:{node.start_point[1]}-{line_end}:{node.end_point[1]}"
        id_string = f"{canonical_path}#{symbol_type}#{name}#{span_str}"
        symbol_id = UUID(hashlib.sha256(id_string.encode()).hexdigest()[:32])

        # Extract signature (first line of the symbol)
        signature = None
        if line_start <= len(lines):
            signature = lines[line_start - 1].strip()

        # Check if exported (simplified - would need more context for full accuracy)
        is_exported = False

        return CodeSymbol(
            name=name,
            symbol_type=symbol_type,
            line_start=line_start,
            line_end=line_end,
            signature=signature,
            docstring=None,  # JavaScript doesn't have standard docstrings
            is_exported=is_exported,
            is_private=name.startswith('_'),
            decorators=[],
            parent=None,
            id=symbol_id
        )

    def _extract_exports(self, root_node, text: str, symbols: list[CodeSymbol]) -> list[APIExport]:
        """Extract export statements from JavaScript code."""
        exports = []
        language = self._get_language()

        # Query for various export patterns
        query = language.query("""
            (export_statement) @export
            (export_clause (export_specifier name: (identifier) @export_name))
            (assignment_expression
                left: (member_expression
                    object: (identifier) @module
                    property: (property_identifier) @exports_prop)
                (#eq? @module "module")
                (#eq? @exports_prop "exports"))
        """)

        captures = query.captures(root_node)

        # Create a symbol name to ID mapping
        symbol_map = {s.name: s.id for s in symbols}

        for node, capture_name in captures:
            if capture_name == 'export_name':
                name = node.text.decode('utf-8')
                export = APIExport(
                    name=name,
                    export_type='unknown',
                    symbol_id=symbol_map.get(name),
                    is_reexport=False,
                    original_module=None,
                    docstring=None
                )
                exports.append(export)

        return exports

    def _calculate_metadata(self, root_node, text: str, symbol_count: int) -> dict[str, Any]:
        """Calculate metadata including complexity metrics."""
        metadata = {}

        # Count control flow nodes for complexity
        language = self._get_language()
        complexity_query = language.query("""
            (if_statement) @if
            (while_statement) @while
            (for_statement) @for
            (switch_statement) @switch
            (catch_clause) @catch
            (binary_expression operator: ["&&" "||"]) @logical
        """)

        captures = complexity_query.captures(root_node)
        complexity = len(captures) + 1  # Base complexity of 1

        metadata['complexity_score'] = complexity
        metadata['symbol_count'] = symbol_count

        return metadata

    def _resolve_import_path(self, import_path: str, file_path: Path, repo_path: Path) -> list[str]:
        """Resolve JavaScript import path."""
        resolved_paths = []

        if import_path.startswith('./') or import_path.startswith('../'):
            # Relative import
            base_dir = file_path.parent
            target_path = (base_dir / import_path).resolve()
        elif import_path.startswith('/'):
            # Absolute import from repo root
            target_path = repo_path / import_path[1:]
        else:
            # Module import from node_modules or similar
            return []

        # Try different extensions
        extensions = self._get_file_extensions()
        for ext in extensions:
            candidate = target_path.with_suffix(ext)
            if candidate.exists() and candidate.is_file():
                try:
                    rel_path = candidate.relative_to(repo_path)
                    resolved_paths.append(str(rel_path))
                except ValueError:
                    pass

        # Try directory with index file
        if target_path.is_dir():
            for index_name in self._get_init_files():
                index_file = target_path / index_name
                if index_file.exists():
                    try:
                        rel_path = index_file.relative_to(repo_path)
                        resolved_paths.append(str(rel_path))
                    except ValueError:
                        pass

        return resolved_paths

    def _get_file_extensions(self) -> list[str]:
        """Get JavaScript file extensions."""
        return ['.js', '.jsx']

    def _get_init_files(self) -> list[str]:
        """Get JavaScript initialization files."""
        return ['index.js', 'index.jsx']
