"""Base class for language parsers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ...domain.models import CodeSymbol, APIExport, FunctionDependency


class LanguageParser(ABC):
    """Abstract base class for language-specific parsers."""

    @abstractmethod
    def extract_dependencies(self, file_path: Path, repo_path: Path) -> list[str]:
        """Extract dependencies from a source file.
        
        Args:
            file_path: Path to the source file
            repo_path: Path to the repository root
            
        Returns:
            List of relative paths to dependencies within the repository
        """
        pass

    def extract_code_structure(self, file_path: Path, repo_path: Path) -> tuple[
        list[CodeSymbol], 
        list[APIExport], 
        list[FunctionDependency],
        list[str],  # imports
        dict[str, any]  # metadata (complexity, etc.)
    ]:
        """Extract detailed code structure information.
        
        Args:
            file_path: Path to the source file
            repo_path: Path to the repository root
            
        Returns:
            Tuple of (symbols, exports, function_deps, imports, metadata)
        """
        # Default implementation returns empty data
        return [], [], [], [], {}

    def _resolve_import_path(self, import_path: str, file_path: Path, repo_path: Path) -> list[str]:
        """Resolve import path to actual file paths with security validation."""
        resolved_paths = []

        # Validate import_path format
        if not self._is_valid_import_path(import_path):
            return []

        # Handle relative imports
        if import_path.startswith('.'):
            base_dir = file_path.parent
            relative_path = import_path.lstrip('.')
            if relative_path:
                target_path = base_dir / relative_path.replace('.', '/')
            else:
                target_path = base_dir
        else:
            # Handle absolute imports from repo root
            target_path = repo_path / import_path.replace('.', '/')

        # Resolve and validate the path
        try:
            resolved_target = target_path.resolve()
            repo_resolved = repo_path.resolve()

            # Ensure target is within repository boundaries
            resolved_target.relative_to(repo_resolved)

            # Continue with existing logic...
            extensions = self._get_file_extensions()
            for ext in extensions:
                candidate = resolved_target.with_suffix(ext)
                if candidate.exists() and candidate.is_file():
                    try:
                        rel_path = candidate.relative_to(repo_resolved)
                        resolved_paths.append(str(rel_path))
                    except ValueError:
                        # File is outside repository - skip
                        continue

        except (ValueError, OSError):
            # Path traversal attempt or invalid path
            return []

        # Try directory with __init__ file
        try:
            if resolved_target.is_dir():
                for init_name in self._get_init_files():
                    init_file = resolved_target / init_name
                    if init_file.exists():
                        try:
                            rel_path = init_file.relative_to(repo_resolved)
                            resolved_paths.append(str(rel_path))
                        except ValueError:
                            # File is outside repository - skip
                            continue
        except (ValueError, OSError):
            # Path traversal attempt or invalid path
            pass

        return resolved_paths

    def _is_valid_import_path(self, import_path: str) -> bool:
        """Validate import path format to prevent injection."""
        # Check for null bytes and control characters
        if '\x00' in import_path or any(ord(c) < 32 for c in import_path if c not in '\t\n'):
            return False

        # Check length limits
        if len(import_path) > 1000:  # Reasonable limit
            return False

        # Check for excessive relative traversal
        if import_path.count('..') > 10:  # Reasonable limit
            return False

        # Must not be empty or whitespace only
        if not import_path.strip():
            return False

        return True

    @abstractmethod
    def _get_file_extensions(self) -> list[str]:
        """Get file extensions for this language."""
        pass

    @abstractmethod
    def _get_init_files(self) -> list[str]:
        """Get initialization file names for this language."""
        pass

    def _all_imports_from_tree(self, root_node) -> list[str]:
        """Generic Tree-sitter traversal to collect import declarations.

        Parsers that need language-specific handling can still override this method.
        This implementation cerca più tipi di nodo comunemente usati.
        """
        imports = []

        IMPORT_NODE_TYPES = {
            "import_declaration", "import_statement", "import", "qualified_import",
        }

        def text_of(node):
            # Concatena ricorsivamente il testo dei token figli, decodificando bytes
            parts = []

            def collect(n):
                if n is None:
                    return
                # Only collect text for leaf nodes/token nodes to avoid joining
                # large subtrees into a single giant string.
                children = getattr(n, "children", []) or []
                if not children:
                    t = getattr(n, "text", None)
                    if isinstance(t, (bytes, bytearray)): 
                        try:
                            t = t.decode("utf-8", errors="ignore")
                        except Exception:
                            t = None
                    if t:
                        s = str(t).strip()
                        # ignore extremely long tokens
                        if s and len(s) <= 200:
                            parts.append(s)
                    return
                for c in children:
                    collect(c)

            collect(node)
            return " ".join(parts).strip()

        def walk(node):
            if node is None:
                return
            try:
                t = getattr(node, "type", "")
                if t in IMPORT_NODE_TYPES:
                    raw = text_of(node)
                    clean = raw.replace("import", "").replace("static", "").replace(";", "").strip()
                    if clean:
                        imports.append(clean)
                # No generic textual fallback here. Parsers that need language-specific
                # extraction should override this method or provide their own fallbacks.
            except Exception:
                # difensivo: non vuole rompere l'intera scansione
                pass

            for child in getattr(node, "children", []) or []:
                walk(child)

        walk(root_node)
        # dedup mantenendo ordine
        seen = set()
        out = []
        for i in imports:
            if i not in seen:
                seen.add(i)
                out.append(i)
        return out


