import hashlib
import logging
from pathlib import Path
from typing import Optional
from uuid import UUID

from tree_sitter import Language as TSLanguage, Parser
import tree_sitter_kotlin
try:
    from tree_sitter import Query, QueryCursor
except Exception:
    Query = None
    QueryCursor = None
from .base import LanguageParser
from ...domain.models import CodeSymbol, APIExport

logger = logging.getLogger(__name__)


class KotlinParser(LanguageParser):
    def __init__(self):
        super().__init__()
        self.language = TSLanguage(tree_sitter_kotlin.language())
        self.parser = Parser(self.language)

    def _get_file_extensions(self) -> set[str]:
        return {".kt", ".kts"}

    def _get_init_files(self) -> set[str]:
        return set()

    def extract_dependencies(self, file_path: Path, repo_path: Path) -> list[str]:
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            raw_imports = self._extract_imports_fallback(content)
            # Resolve imports to repository-relative paths where possible
            resolved_imports = []
            for imp in raw_imports:
                try:
                    res = self._resolve_kotlin_import(imp, repo_path)
                    if res:
                        resolved_imports.append(res)
                except Exception:
                    continue
            # Resolve import strings to repository-relative paths when possible
            resolved = []
            for imp in raw_imports:
                try:
                    res = self._resolve_kotlin_import(imp, repo_path)
                    if res:
                        resolved.append(res)
                except Exception:
                    # If resolution fails, ignore and keep the raw import elsewhere
                    continue
            return list(set(resolved))
        except Exception as e:
            logger.exception("Failed to extract dependencies for %s: %s", file_path, e)
            return []

    def _resolve_kotlin_import(self, import_name: str, repo_path: Path) -> Optional[str]:
        clean_import = import_name.replace('.*', '').strip()
        rel_path_str = clean_import.replace('.', '/') + ".kt"
        for root in ["app/src/main/java", "app/src/main/kotlin", "src/main/kotlin"]:
            candidate = Path(root) / rel_path_str
            if (repo_path / candidate).exists(): return str(candidate)
        return None

    def _extract_imports_fallback(self, content: str) -> list[str]:
        imports = []
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("import "):
                clean = line.replace("import ", "").replace(";", "").strip()
                if clean:
                    imports.append(clean)
        return list(set(imports))

    def extract_code_structure(self, file_path: Path, repo_path: Path) -> tuple:
        try:
            if not file_path.is_file(): return [], [], [], [], {}
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            tree = self.parser.parse(content.encode('utf-8'))

            raw_imports = self._extract_imports_fallback(content)
            # Resolve imports to repository-relative paths where possible
            resolved_imports = []
            for imp in raw_imports:
                try:
                    res = self._resolve_kotlin_import(imp, repo_path)
                    if res:
                        resolved_imports.append(res)
                except Exception:
                    continue

            symbols = []
            complexity = 1
            file_path_str = str(file_path)
            comp_nodes = ('if_expression', 'for_statement', 'while_statement', 'when_entry', 'catch_clause')

            def traverse(node):
                nonlocal complexity
                if node.type in comp_nodes:
                    complexity += 1

                if node.type in ('class_declaration', 'function_declaration', 'object_declaration'):
                    name = None
                    for child in node.children:
                        if child.type in ('identifier', 'type_identifier', 'simple_identifier'):
                            name = child.text.decode('utf-8', errors='ignore')
                            break

                    if name:
                        kind = 'function' if node.type == 'function_declaration' else 'class'
                        line_start = node.start_point[0] + 1
                        symbol_id = UUID(
                            bytes=hashlib.sha256(f"{file_path_str}:{name}:{line_start}".encode()).digest()[:16])
                        symbols.append(CodeSymbol(name=name, symbol_type=kind, line_start=line_start,
                                                  line_end=node.end_point[0] + 1, signature=name, is_exported=True,
                                                  id=symbol_id))
                for c in node.children:
                    traverse(c)

            traverse(tree.root_node)

            # Try to compute complexity using Query if available (like JS parser)
            try:
                if Query and QueryCursor:
                    complexity_query = Query(self.language, """
                        (if_expression) @if
                        (while_statement) @while
                        (for_statement) @for
                        (when_entry) @when
                        (catch_clause) @catch
                        (binary_expression operator: ["&&" "||"]) @logical
                    """)
                    cursor = QueryCursor(complexity_query)
                    captures_dict = cursor.captures(tree.root_node)
                    total_captures = sum(len(nodes) for nodes in captures_dict.values())
                    complexity = total_captures + 1
                else:
                    # already counted via traversal
                    complexity = complexity
            except Exception:
                # keep traversal result if query fails
                complexity = complexity

            exports = [APIExport(name=s.name, export_type=s.symbol_type, symbol_id=s.id) for s in symbols]

            total_classes = sum(1 for s in symbols if s.symbol_type == 'class')
            total_functions = sum(1 for s in symbols if s.symbol_type == 'function')

            metadata = {
                'lines_of_code': len(content.splitlines()),
                'complexity_score': complexity,
                'total_classes': total_classes,
                'total_functions': total_functions,
                'symbol_count': len(symbols)
            }

            # Third element: function-level dependencies (none implemented)
            # Fourth element: imports (resolved paths where possible)
            function_deps: list[any] = []
            imports_list = resolved_imports if resolved_imports else raw_imports

            return symbols, exports, function_deps, imports_list, metadata

        except Exception:
            return [], [], [], [], {}