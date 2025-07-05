"""Go dependency parser using go list command."""

import json
import logging
import subprocess
from pathlib import Path

from .base import LanguageParser

logger = logging.getLogger(__name__)


class GoParser(LanguageParser):
    """Parser for Go files using go list command."""

    def extract_dependencies(self, file_path: Path, repo_path: Path) -> list[str]:
        """Extract Go dependencies using go list."""
        dependencies = []

        try:
            # Validate and resolve repo_path
            validated_repo_path = self._validate_repo_path(repo_path)

            # Run go list to get package information
            result = subprocess.run(
                ['go', 'list', '-json', './...'],
                check=False, cwd=validated_repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                logger.warning(f"go list failed: {result.stderr}")
                return []

            # Parse JSON output
            packages = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        pkg_info = json.loads(line)
                        packages.append(pkg_info)
                    except json.JSONDecodeError:
                        continue

            # Find the package containing our file
            relative_path = file_path.relative_to(repo_path)
            file_package = None

            for pkg in packages:
                if 'GoFiles' in pkg:
                    pkg_dir = Path(pkg.get('Dir', ''))
                    for go_file in pkg['GoFiles']:
                        if pkg_dir / go_file == file_path:
                            file_package = pkg
                            break
                    if file_package:
                        break

            if not file_package:
                return []

            # Get imports for this package
            imports = file_package.get('Imports', [])

            # Filter for local imports (within the repository)
            module_path = file_package.get('Module', {}).get('Path', '')

            for imp in imports:
                if imp.startswith(module_path):
                    # This is a local import
                    # Find the corresponding package
                    for pkg in packages:
                        if pkg.get('ImportPath') == imp:
                            pkg_dir = Path(pkg.get('Dir', ''))
                            go_files = pkg.get('GoFiles', [])

                            # Add all Go files in the package
                            for go_file in go_files:
                                dep_path = pkg_dir / go_file
                                if dep_path.exists():
                                    try:
                                        rel_path = dep_path.relative_to(repo_path)
                                        dependencies.append(str(rel_path))
                                    except ValueError:
                                        pass
                            break

        except subprocess.TimeoutExpired:
            logger.warning("go list command timed out")
        except Exception as e:
            logger.warning(f"Failed to parse Go file {file_path}: {e}")

        return dependencies

    def _validate_repo_path(self, repo_path: Path) -> Path:
        """Validate and resolve repository path."""
        # Resolve to absolute path to prevent traversal
        resolved_path = repo_path.resolve()

        # Ensure it's actually a directory
        if not resolved_path.is_dir():
            raise ValueError(f"Repository path is not a directory: {resolved_path}")

        # Ensure it contains a Go module (go.mod file)
        if not (resolved_path / "go.mod").exists():
            # Look for any .go files to confirm it's a Go project
            go_files = list(resolved_path.rglob("*.go"))
            if not go_files:
                raise ValueError(f"No Go files found in repository: {resolved_path}")

        return resolved_path

    def _get_file_extensions(self) -> list[str]:
        """Get Go file extensions."""
        return ['.go']

    def _get_init_files(self) -> list[str]:
        """Get Go initialization files."""
        return []
