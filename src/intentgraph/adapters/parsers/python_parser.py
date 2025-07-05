"""Python dependency parser using grimp."""

import logging
from pathlib import Path

import grimp

from .base import LanguageParser

logger = logging.getLogger(__name__)


class PythonParser(LanguageParser):
    """Parser for Python files using grimp."""

    def __init__(self):
        self._graph_cache = {}

    def extract_dependencies(self, file_path: Path, repo_path: Path) -> list[str]:
        """Extract Python dependencies using grimp."""
        dependencies = []
        repo_key = str(repo_path)

        try:
            # Use cached grimp graph or build new one
            if repo_key not in self._graph_cache:
                try:
                    self._graph_cache[repo_key] = grimp.build_graph(str(repo_path))
                except Exception:
                    return self._fallback_parse(file_path, repo_path)

            graph = self._graph_cache[repo_key]

            # Get relative module path
            relative_path = file_path.relative_to(repo_path)
            module_path = str(relative_path.with_suffix(''))
            module_name = module_path.replace('/', '.')

            # Remove __init__ from module name
            if module_name.endswith('.__init__'):
                module_name = module_name[:-9]

            # Get direct dependencies
            try:
                direct_deps = graph.get_dependencies(module_name)

                for dep in direct_deps:
                    # Convert module name back to file path
                    dep_path = dep.replace('.', '/') + '.py'

                    # Check if it's an __init__ file
                    init_path = dep.replace('.', '/') + '/__init__.py'

                    # Check which file exists
                    if (repo_path / dep_path).exists():
                        dependencies.append(dep_path)
                    elif (repo_path / init_path).exists():
                        dependencies.append(init_path)

            except grimp.exceptions.ModuleNotPresent:
                logger.debug(f"Module not found in graph: {module_name}")

        except Exception as e:
            logger.warning(f"Failed to analyze Python file {file_path}: {e}")
            # Fallback to simple parsing
            dependencies.extend(self._fallback_parse(file_path, repo_path))

        return dependencies

    def _fallback_parse(self, file_path: Path, repo_path: Path) -> list[str]:
        """Fallback parser using simple AST parsing."""
        import ast

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
                        # Handle relative imports
                        if node.level > 0:
                            # Relative import
                            base_path = file_path.parent
                            for _ in range(node.level - 1):
                                base_path = base_path.parent

                            if node.module:
                                import_path = f"{'.' * node.level}{node.module}"
                            else:
                                import_path = '.' * node.level
                        else:
                            # Absolute import
                            import_path = node.module

                        deps = self._resolve_import_path(import_path, file_path, repo_path)
                        dependencies.extend(deps)

        except Exception as e:
            logger.warning(f"Fallback parsing failed for {file_path}: {e}")

        return dependencies

    def _get_file_extensions(self) -> list[str]:
        """Get Python file extensions."""
        return ['.py']

    def _get_init_files(self) -> list[str]:
        """Get Python initialization files."""
        return ['__init__.py']
