"""TypeScript dependency parser using tree-sitter."""

import hashlib
import logging
from pathlib import Path
from typing import Optional, Any
from uuid import UUID, uuid4

from .base import LanguageParser
from ...domain.models import CodeSymbol, APIExport, FunctionDependency

logger = logging.getLogger(__name__)


class TypeScriptParser(LanguageParser):
    """Parser for TypeScript files using tree-sitter with lazy initialization."""

    def __init__(self):
        self._language = None
        self._parser = None
        self._init_error = None
        self._symbol_map = {}  # Maps symbol names to UUIDs

    def _ensure_initialized(self) -> bool:
        """Lazy initialization of tree-sitter components."""
        if self._parser is not None:
            return True
        if self._init_error is not None:
            return False

        try:
            from tree_sitter_language_pack import get_language, get_parser
            self._language = get_language('typescript')
            self._parser = get_parser('typescript')
            return True
        except Exception as e:
            self._init_error = e
            logger.warning(f"Failed to initialize tree-sitter for TypeScript: {e}")
            return False

    def extract_dependencies(self, file_path: Path, repo_path: Path) -> list[str]:
        """Extract TypeScript dependencies using tree-sitter."""
        if not self._ensure_initialized():
            logger.warning(f"Cannot extract dependencies from {file_path}: tree-sitter not available")
            return []

        dependencies = []

        try:
            content = file_path.read_bytes()
            tree = self._parser.parse(content)

            # Query for import statements
            query = self._language.query("""
                (import_statement source: (string) @import)
                (call_expression
                    function: (identifier) @func
                    arguments: (arguments (string) @require)
                    (#eq? @func "require"))
                (import_statement
                    source: (string) @dynamic_import)
            """)

            captures = query.captures(tree.root_node)

            for node, capture_name in captures:
                if capture_name in ['import', 'require', 'dynamic_import']:
                    import_path = node.text.decode('utf-8').strip('"\'')

                    # Skip external modules
                    if not import_path.startswith('.') and not import_path.startswith('/'):
                        continue

                    deps = self._resolve_import_path(import_path, file_path, repo_path)
                    dependencies.extend(deps)

        except Exception as e:
            logger.warning(f"Failed to parse TypeScript file {file_path}: {e}")

        return dependencies

    def extract_code_structure(self, file_path: Path, repo_path: Path) -> tuple[
        list[CodeSymbol],
        list[APIExport],
        list[FunctionDependency],
        list[str],  # imports
        dict[str, Any]  # metadata
    ]:
        """Extract detailed code structure from TypeScript file.

        Returns:
            Tuple of (symbols, exports, function_deps, imports, metadata)
        """
        if not self._ensure_initialized():
            logger.warning(f"Cannot extract code structure from {file_path}: tree-sitter not available")
            return [], [], [], [], {}

        try:
            content = file_path.read_text(encoding='utf-8')
            content_bytes = content.encode('utf-8')
            tree = self._parser.parse(content_bytes)

            # Extract symbols (pass file_path for deterministic IDs)
            symbols = self._extract_symbols(tree.root_node, file_path, content)

            # Build symbol map for dependencies
            self._symbol_map = {s.name: s.id for s in symbols}

            # Extract imports
            imports = self._extract_imports(tree.root_node)

            # Extract exports
            exports = self._extract_api_exports(tree.root_node, symbols)

            # Calculate metadata
            metadata = self._calculate_metadata(tree.root_node, content)

            # Sort for determinism
            symbols = sorted(symbols, key=lambda s: (s.line_start, s.symbol_type, s.name))
            exports = sorted(exports, key=lambda e: e.name)
            imports = sorted(imports)

            return symbols, exports, [], imports, metadata

        except Exception as e:
            logger.warning(f"Failed to extract code structure from {file_path}: {e}")
            return [], [], [], [], {}

    def _extract_symbols(self, node, file_path: Path, content: str) -> list[CodeSymbol]:
        """Extract all code symbols from the AST."""
        symbols = []
        file_path_str = str(file_path)

        def traverse(node, parent=None):
            node_type = node.type

            # Functions
            if node_type in ('function_declaration', 'method_definition', 'arrow_function'):
                symbol = self._create_function_symbol(node, file_path_str, content, parent)
                if symbol:
                    symbols.append(symbol)
                    traverse_children(node, symbol.name)
                    return

            # Classes
            elif node_type == 'class_declaration':
                symbol = self._create_class_symbol(node, file_path_str, content)
                if symbol:
                    symbols.append(symbol)
                    traverse_children(node, symbol.name)
                    return

            # Interfaces
            elif node_type == 'interface_declaration':
                symbol = self._create_interface_symbol(node, file_path_str, content)
                if symbol:
                    symbols.append(symbol)

            # Type aliases
            elif node_type == 'type_alias_declaration':
                symbol = self._create_type_symbol(node, file_path_str, content)
                if symbol:
                    symbols.append(symbol)

            # Enums
            elif node_type == 'enum_declaration':
                symbol = self._create_enum_symbol(node, file_path_str, content)
                if symbol:
                    symbols.append(symbol)

            traverse_children(node, parent)

        def traverse_children(node, parent):
            for child in node.children:
                traverse(child, parent)

        traverse(node)
        return symbols

    def _create_function_symbol(self, node, file_path_str: str, content: str, parent: Optional[str] = None) -> Optional[CodeSymbol]:
        """Create a CodeSymbol for a function."""
        try:
            # Get function name
            name_node = self._find_child_by_field(node, 'name')
            if not name_node:
                return None
            name = self._get_node_text(name_node, content)

            # Get signature
            signature = self._get_node_text(node, content).split('\n')[0][:200]  # First line, truncated

            # Determine if exported
            is_exported = self._is_exported(node)
            is_private = name.startswith('_')

            # Get position
            line_start = node.start_point[0] + 1
            line_end = node.end_point[0] + 1

            # Generate deterministic ID
            symbol_id = self._generate_symbol_id(file_path_str, 'function', name, line_start)

            return CodeSymbol(
                name=name,
                symbol_type='function',
                line_start=line_start,
                line_end=line_end,
                signature=signature,
                is_exported=is_exported,
                is_private=is_private,
                parent=parent,
                id=symbol_id
            )
        except Exception as e:
            logger.debug(f"Failed to create function symbol: {e}")
            return None

    def _create_class_symbol(self, node, file_path_str: str, content: str) -> Optional[CodeSymbol]:
        """Create a CodeSymbol for a class."""
        try:
            # Get class name
            name_node = self._find_child_by_field(node, 'name')
            if not name_node:
                return None
            name = self._get_node_text(name_node, content)

            # Get signature (simplified)
            signature = f"class {name}"

            # Determine if exported
            is_exported = self._is_exported(node)
            is_private = name.startswith('_')

            # Get position
            line_start = node.start_point[0] + 1
            line_end = node.end_point[0] + 1

            # Generate deterministic ID
            symbol_id = self._generate_symbol_id(file_path_str, 'class', name, line_start)

            return CodeSymbol(
                name=name,
                symbol_type='class',
                line_start=line_start,
                line_end=line_end,
                signature=signature,
                is_exported=is_exported,
                is_private=is_private,
                id=symbol_id
            )
        except Exception as e:
            logger.debug(f"Failed to create class symbol: {e}")
            return None

    def _create_interface_symbol(self, node, file_path_str: str, content: str) -> Optional[CodeSymbol]:
        """Create a CodeSymbol for an interface."""
        try:
            # Get interface name
            name_node = self._find_child_by_field(node, 'name')
            if not name_node:
                return None
            name = self._get_node_text(name_node, content)

            # Get signature
            signature = f"interface {name}"

            # Determine if exported
            is_exported = self._is_exported(node)

            # Get position
            line_start = node.start_point[0] + 1
            line_end = node.end_point[0] + 1

            # Generate deterministic ID
            symbol_id = self._generate_symbol_id(file_path_str, 'interface', name, line_start)

            return CodeSymbol(
                name=name,
                symbol_type='interface',
                line_start=line_start,
                line_end=line_end,
                signature=signature,
                is_exported=is_exported,
                id=symbol_id
            )
        except Exception as e:
            logger.debug(f"Failed to create interface symbol: {e}")
            return None

    def _create_type_symbol(self, node, file_path_str: str, content: str) -> Optional[CodeSymbol]:
        """Create a CodeSymbol for a type alias."""
        try:
            # Get type name
            name_node = self._find_child_by_field(node, 'name')
            if not name_node:
                return None
            name = self._get_node_text(name_node, content)

            # Get signature (simplified)
            signature = f"type {name}"

            # Determine if exported
            is_exported = self._is_exported(node)

            # Get position
            line_start = node.start_point[0] + 1
            line_end = node.end_point[0] + 1

            # Generate deterministic ID
            symbol_id = self._generate_symbol_id(file_path_str, 'type', name, line_start)

            return CodeSymbol(
                name=name,
                symbol_type='type',
                line_start=line_start,
                line_end=line_end,
                signature=signature,
                is_exported=is_exported,
                id=symbol_id
            )
        except Exception as e:
            logger.debug(f"Failed to create type symbol: {e}")
            return None

    def _create_enum_symbol(self, node, file_path_str: str, content: str) -> Optional[CodeSymbol]:
        """Create a CodeSymbol for an enum."""
        try:
            # Get enum name
            name_node = self._find_child_by_field(node, 'name')
            if not name_node:
                return None
            name = self._get_node_text(name_node, content)

            # Get signature
            signature = f"enum {name}"

            # Determine if exported
            is_exported = self._is_exported(node)

            # Get position
            line_start = node.start_point[0] + 1
            line_end = node.end_point[0] + 1

            # Generate deterministic ID
            symbol_id = self._generate_symbol_id(file_path_str, 'enum', name, line_start)

            return CodeSymbol(
                name=name,
                symbol_type='enum',
                line_start=line_start,
                line_end=line_end,
                signature=signature,
                is_exported=is_exported,
                id=symbol_id
            )
        except Exception as e:
            logger.debug(f"Failed to create enum symbol: {e}")
            return None

    def _extract_imports(self, node) -> list[str]:
        """Extract all import statements."""
        imports = []

        def traverse(node):
            if node.type == 'import_statement':
                import_text = self._reconstruct_import(node)
                if import_text:
                    imports.append(import_text)

            for child in node.children:
                traverse(child)

        traverse(node)
        return imports

    def _reconstruct_import(self, node) -> Optional[str]:
        """Reconstruct import statement as string."""
        try:
            # Find the string literal (source)
            source_node = self._find_child_by_field(node, 'source')
            if source_node:
                source = source_node.text.decode('utf-8').strip('"\'')
                return f"import ... from '{source}'"
            return None
        except Exception:
            return None

    def _extract_api_exports(self, node, symbols: list[CodeSymbol]) -> list[APIExport]:
        """Extract exported APIs."""
        exports = []
        exported_names = set()

        def traverse(node):
            # Check for export keywords
            if node.type in ('export_statement', 'export_declaration'):
                # Get exported names
                for child in node.children:
                    if child.type in ('function_declaration', 'class_declaration',
                                     'interface_declaration', 'type_alias_declaration',
                                     'enum_declaration'):
                        name_node = self._find_child_by_field(child, 'name')
                        if name_node:
                            exported_names.add(name_node.text.decode('utf-8'))

            for child in node.children:
                traverse(child)

        traverse(node)

        # Create exports for exported symbols
        for symbol in symbols:
            if symbol.name in exported_names or symbol.is_exported:
                export = APIExport(
                    name=symbol.name,
                    export_type=symbol.symbol_type,
                    symbol_id=symbol.id
                )
                exports.append(export)

        return exports

    def _calculate_metadata(self, node, content: str) -> dict[str, Any]:
        """Calculate code metrics."""
        metadata = {
            'total_functions': 0,
            'total_classes': 0,
            'total_interfaces': 0,
            'total_types': 0,
            'total_enums': 0,
            'lines_of_code': len([line for line in content.splitlines() if line.strip()])
        }

        def traverse(node):
            if node.type in ('function_declaration', 'method_definition', 'arrow_function'):
                metadata['total_functions'] += 1
            elif node.type == 'class_declaration':
                metadata['total_classes'] += 1
            elif node.type == 'interface_declaration':
                metadata['total_interfaces'] += 1
            elif node.type == 'type_alias_declaration':
                metadata['total_types'] += 1
            elif node.type == 'enum_declaration':
                metadata['total_enums'] += 1

            for child in node.children:
                traverse(child)

        traverse(node)
        return metadata

    def _is_exported(self, node) -> bool:
        """Check if node is exported."""
        # Traverse up to parent to check for export keyword
        parent = node.parent
        while parent:
            if parent.type in ('export_statement', 'export_declaration'):
                return True
            parent = parent.parent
        return False

    def _find_child_by_field(self, node, field_name: str):
        """Find child node by field name."""
        return node.child_by_field_name(field_name)

    def _get_node_text(self, node, content: str) -> str:
        """Get text content of a node."""
        return node.text.decode('utf-8')

    def _generate_symbol_id(self, file_path: str, kind: str, name: str, line: int) -> UUID:
        """Generate deterministic symbol ID using SHA256."""
        canonical = f"{file_path}:{kind}:{name}:{line}"
        hash_bytes = hashlib.sha256(canonical.encode('utf-8')).digest()
        # Convert first 16 bytes to UUID
        return UUID(bytes=hash_bytes[:16])

    def _resolve_import_path(self, import_path: str, file_path: Path, repo_path: Path) -> list[str]:
        """Resolve TypeScript import path."""
        resolved_paths = []

        if import_path.startswith('./') or import_path.startswith('../'):
            # Relative import
            base_dir = file_path.parent
            target_path = (base_dir / import_path).resolve()
        elif import_path.startswith('/'):
            # Absolute import from repo root
            target_path = repo_path / import_path[1:]
        else:
            # Module import
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
        """Get TypeScript file extensions."""
        return ['.ts', '.tsx', '.js', '.jsx']

    def _get_init_files(self) -> list[str]:
        """Get TypeScript initialization files."""
        return ['index.ts', 'index.tsx', 'index.js', 'index.jsx']
