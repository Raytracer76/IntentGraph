import hashlib
import logging
from pathlib import Path
from typing import Optional
from uuid import UUID

from tree_sitter import Language as TSLanguage, Parser
import tree_sitter_java
try:
    from tree_sitter import Query, QueryCursor
except Exception:
    Query = None
    QueryCursor = None
from .base import LanguageParser
from ...domain.models import CodeSymbol, APIExport

logger = logging.getLogger(__name__)


class JavaParser(LanguageParser):
    def __init__(self):
        super().__init__()
        self.language = TSLanguage(tree_sitter_java.language())
        self.parser = Parser(self.language)

    def _get_file_extensions(self) -> set[str]:
        return {".java"}

    def _get_init_files(self) -> set[str]:
        return set()

    def extract_dependencies(self, file_path: Path, repo_path: Path) -> list[str]:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            raw_imports: list[str] = []

            # Prefer tree-sitter extraction when parser is available; fall back to
            # textual scanning if anything goes wrong. The base class provides
            # a robust _all_imports_from_tree implementation.
            try:
                tree = self.parser.parse(content.encode("utf-8"))
                raw_imports = self._all_imports_from_tree(tree.root_node) or []
            except Exception:
                # If tree-sitter parsing fails, fall back to the simple line-based
                # extractor to avoid losing all import information.
                raw_imports = self._extract_imports_fallback(content)

            # Normalize imports to a canonical dotted form (tree-sitter tokens
            # sometimes introduce spaces around dots). This keeps things like
            # "android . os . Bundle" -> "android.os.Bundle" so resolution
            # and sanitization work correctly.
            import re
            def normalize_imp(s: str) -> str:
                if not s:
                    return s
                # collapse surrounding whitespace around dots
                s = re.sub(r"\s*\.\s*", ".", s)
                # collapse remaining whitespace
                s = re.sub(r"\s+", " ", s).strip()
                return s

            resolved: list[str] = []
            for imp in raw_imports:
                imp = normalize_imp(imp)
                try:
                    res = self._resolve_java_import(imp, repo_path)
                    if res:
                        resolved.append(res)
                except Exception:
                    # defensive: skip problematic import strings
                    continue
            return list(dict.fromkeys(resolved))
        except Exception as e:
            logger.exception("Failed to extract dependencies for %s: %s", file_path, e)
            return []

    def _resolve_java_import(self, import_name: str, repo_path: Path) -> Optional[str]:
        # sanitize input: reject very long or malformed import strings early
        if not import_name:
            return None

        # quick length and content guard
        if len(import_name) > 300:
            logger.debug("Skipping overly long import string: %r", import_name[:200])
            return None
        # sanitize to a canonical dotted name (or None)
        sanitized = self._sanitize_import_name(import_name)
        if not sanitized:
            logger.debug("Import string not recognized as valid Java import: %r", import_name)
            return None

        clean_import = sanitized.replace('.*', '').strip()
        # remove any trailing dot that may remain after stripping wildcards
        if clean_import.endswith('.'):
            clean_import = clean_import.rstrip('.')
        rel_path_str = clean_import.replace('.', '/') + ".java"
        for root in ["app/src/main/java", "src/main/java"]:
            candidate = Path(root) / rel_path_str
            try:
                if (repo_path / candidate).exists():
                    return str(candidate)
            except OSError as e:
                logger.debug("OS error checking candidate %s: %s", candidate, e)
                continue
        return None

    def extract_code_structure(self, file_path: Path, repo_path: Path) -> tuple:
        try:
            if not file_path.is_file():
                return [], [], [], [], {}
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            tree = self.parser.parse(content.encode('utf-8'))

            # Try to extract imports from the parsed tree first (more accurate),
            # otherwise fall back to a simple textual extractor.
            raw_imports: list[str] = []
            try:
                tree = self.parser.parse(content.encode('utf-8'))
                raw_imports = self._all_imports_from_tree(tree.root_node) or []
                # normalize any imports produced by the generic tree traverser
                import re
                raw_imports = [re.sub(r"\s*\.\s*", ".", i).strip() if i else i for i in raw_imports]
            except Exception:
                raw_imports = self._extract_imports_fallback(content)

            symbols = []
            file_path_str = str(file_path)

            # We'll extract symbols with a traversal and compute complexity using
            # a Tree-sitter Query (if available) mirroring the JavaScript parser.
            complexity = 1

            def traverse(node):
                name_node = node.child_by_field_name('name')
                if name_node:
                    try:
                        name = name_node.text.decode('utf-8', errors='ignore')
                    except Exception:
                        name = None
                    if name:
                        kind = 'function' if node.type == 'method_declaration' else 'class'
                        line_start = node.start_point[0] + 1
                        symbol_id = UUID(
                            bytes=hashlib.sha256(f"{file_path_str}:{name}:{line_start}".encode()).digest()[:16])
                        symbols.append(CodeSymbol(name=name, symbol_type=kind, line_start=line_start,
                                                  line_end=node.end_point[0] + 1, signature=name, is_exported=True,
                                                  id=symbol_id))
                for c in node.children:
                    traverse(c)

            traverse(tree.root_node)

            # Try to compute complexity using Query like JavaScript parser.
            try:
                if Query and QueryCursor:
                    complexity_query = Query(self.language, """
                        (if_statement) @if
                        (while_statement) @while
                        (for_statement) @for
                        (switch_statement) @switch
                        (switch_expression) @switch_expr
                        (catch_clause) @catch
                        (binary_expression operator: ["&&" "||"]) @logical
                    """)

                    cursor = QueryCursor(complexity_query)
                    captures_dict = cursor.captures(tree.root_node)
                    total_captures = sum(len(nodes) for nodes in captures_dict.values())
                    complexity = total_captures + 1
                else:
                    # Fallback: simple traversal count for common control nodes
                    comp_nodes = (
                        'if_statement', 'for_statement', 'while_statement',
                        'switch_expression', 'switch_statement', 'catch_clause', 'conditional_expression'
                    )
                    count = 0
                    nodes = [tree.root_node]
                    while nodes:
                        n = nodes.pop()
                        if n.type in comp_nodes:
                            count += 1
                        nodes.extend(n.children)
                    complexity = count + 1
            except Exception:
                # If anything goes wrong, keep baseline complexity
                complexity = complexity

            exports = [APIExport(name=s.name, export_type=s.symbol_type, symbol_id=s.id) for s in symbols]

            total_classes = sum(1 for s in symbols if s.symbol_type == 'class')
            total_functions = sum(1 for s in symbols if s.symbol_type == 'function')

            metadata = {
                'lines_of_code': len(content.splitlines()),
                # Provide complexity_score for compatibility with services and other parsers
                'complexity_score': complexity,
                'total_classes': total_classes,
                'total_functions': total_functions,
                'symbol_count': len(symbols)
            }

            return symbols, exports, [], raw_imports, metadata
        except Exception as e:
            logger.exception("Failed to extract code structure for %s: %s", file_path, e)
            return [], [], [], [], {}

    def _extract_imports_fallback(self, content: str) -> list[str]:
        imports: list[str] = []
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("/*") or line.startswith("*"):
                continue
            if line.startswith("import "):
                clean = line[len("import "):].strip()
                if ";" in clean:
                    clean = clean.split(";", 1)[0].strip()
                if " //" in clean:
                    clean = clean.split(" //", 1)[0].strip()
                if clean:
                    imports.append(clean)
        seen = set()
        out = []
        for i in imports:
            if i not in seen:
                seen.add(i)
                out.append(i)
        return out

    def _sanitize_import_name(self, import_name: str) -> Optional[str]:
        import re
        if not import_name or '\n' in import_name or '\r' in import_name:
            return None
        s = import_name.strip()
        if s.startswith("static "):
            s = s[len("static "):].strip()
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)(?:\.[A-Za-z_][A-Za-z0-9_]*)*(?:\.\*)?$", s)
        if m:
            return s
        return None

