"""TypeScript dependency parser using tree-sitter."""

import logging
from pathlib import Path

from tree_sitter_language_pack import get_language, get_parser

from .base import LanguageParser

logger = logging.getLogger(__name__)


class TypeScriptParser(LanguageParser):
    """Parser for TypeScript files using tree-sitter."""

    def __init__(self):
        self.language = get_language('typescript')
        self.parser = get_parser('typescript')

    def extract_dependencies(self, file_path: Path, repo_path: Path) -> list[str]:
        """Extract TypeScript dependencies using tree-sitter."""
        dependencies = []

        try:
            content = file_path.read_bytes()
            tree = self.parser.parse(content)

            # Query for import statements
            query = self.language.query("""
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
