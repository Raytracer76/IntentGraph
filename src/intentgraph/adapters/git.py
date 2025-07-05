"""Git integration and gitignore handling."""

import logging
from pathlib import Path

import pathspec
from git import Repo

logger = logging.getLogger(__name__)


class GitIgnoreHandler:
    """Handles .gitignore file parsing and matching."""

    def __init__(self) -> None:
        self._spec: pathspec.PathSpec | None = None
        self._repo_path: Path | None = None

    def load_gitignore(self, repo_path: Path) -> None:
        """Load .gitignore patterns from repository."""
        self._repo_path = repo_path
        patterns = []

        try:
            # Load .gitignore from root
            gitignore_path = repo_path / ".gitignore"
            if gitignore_path.exists():
                patterns.extend(gitignore_path.read_text(encoding="utf-8").splitlines())

            # Load nested .gitignore files
            for gitignore_file in repo_path.rglob(".gitignore"):
                if gitignore_file != gitignore_path:
                    try:
                        relative_dir = gitignore_file.parent.relative_to(repo_path)
                        nested_patterns = gitignore_file.read_text(encoding="utf-8").splitlines()

                        # Prefix patterns with relative directory
                        for pattern in nested_patterns:
                            if pattern.strip() and not pattern.startswith("#"):
                                if pattern.startswith("/"):
                                    # Absolute pattern within the nested directory
                                    patterns.append(str(relative_dir / pattern[1:]))
                                else:
                                    # Relative pattern
                                    patterns.append(str(relative_dir / pattern))
                    except Exception as e:
                        logger.warning(f"Failed to load {gitignore_file}: {e}")

            # Add common patterns
            patterns.extend([
                ".git/",
                ".git/**",
                "__pycache__/",
                "*.pyc",
                "*.pyo",
                "*.pyd",
                ".Python",
                "build/",
                "develop-eggs/",
                "dist/",
                "downloads/",
                "eggs/",
                ".eggs/",
                "lib/",
                "lib64/",
                "parts/",
                "sdist/",
                "var/",
                "wheels/",
                "*.egg-info/",
                ".installed.cfg",
                "*.egg",
                "node_modules/",
                ".env",
                ".venv/",
                "env/",
                "venv/",
                "ENV/",
                "env.bak/",
                "venv.bak/",
            ])

            # Create pathspec
            self._spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)

        except Exception as e:
            logger.warning(f"Failed to load .gitignore: {e}")
            self._spec = pathspec.PathSpec.from_lines("gitwildmatch", [])

    def is_ignored(self, file_path: Path, repo_path: Path) -> bool:
        """Check if file should be ignored according to .gitignore."""
        if not self._spec or not self._repo_path:
            return False

        try:
            # Get relative path from repository root
            relative_path = file_path.relative_to(repo_path)

            # Check if file matches any ignore pattern
            return self._spec.match_file(str(relative_path))

        except ValueError:
            # File is outside repository
            return True
        except Exception as e:
            logger.warning(f"Error checking ignore status for {file_path}: {e}")
            return False

    def get_tracked_files(self, repo_path: Path) -> list[Path]:
        """Get list of files tracked by Git."""
        try:
            repo = Repo(repo_path)
            tracked_files = []

            for item in repo.index.entries:
                file_path = repo_path / item[0]
                if file_path.exists():
                    tracked_files.append(file_path)

            return tracked_files

        except Exception as e:
            logger.warning(f"Failed to get tracked files: {e}")
            return []
