"""Runtime and tooling detection for RepoSnapshot.

Discovery-only - no execution, no network calls.
All detections are based on file presence and content parsing.
"""

import json
import tomllib
from pathlib import Path

from .models import PackageManager, ToolingInfo, WorkspaceType


class RuntimeDetector:
    """Detects runtime environment and tooling configuration."""

    def __init__(self, repo_root: Path) -> None:
        """Initialize detector with repository root.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root

    def detect_package_manager(self) -> PackageManager:
        """Detect the primary package manager.

        Priority order:
        1. pnpm-lock.yaml → pnpm
        2. package-lock.json → npm
        3. yarn.lock → yarn
        4. poetry.lock → poetry
        5. Pipfile.lock → pipenv
        6. requirements.txt + pip
        7. pyproject.toml → poetry or pip
        8. environment.yml → conda

        Returns:
            Detected PackageManager enum
        """
        # Node.js package managers
        if (self.repo_root / "pnpm-lock.yaml").exists():
            return PackageManager.PNPM
        if (self.repo_root / "package-lock.json").exists():
            return PackageManager.NPM
        if (self.repo_root / "yarn.lock").exists():
            return PackageManager.YARN

        # Python package managers
        if (self.repo_root / "poetry.lock").exists():
            return PackageManager.POETRY
        if (self.repo_root / "Pipfile.lock").exists():
            return PackageManager.PIPENV
        if (self.repo_root / "environment.yml").exists():
            return PackageManager.CONDA
        if (self.repo_root / "requirements.txt").exists():
            return PackageManager.PIP

        # Check pyproject.toml for poetry
        pyproject = self.repo_root / "pyproject.toml"
        if pyproject.exists():
            try:
                with open(pyproject, "rb") as f:
                    data = tomllib.load(f)
                    if "tool" in data and "poetry" in data["tool"]:
                        return PackageManager.POETRY
                    # Default to pip for Python projects
                    return PackageManager.PIP
            except Exception:
                pass

        return PackageManager.UNKNOWN

    def detect_workspace_type(self) -> WorkspaceType:
        """Detect workspace/monorepo configuration.

        Checks for:
        - pnpm-workspace.yaml
        - package.json with "workspaces"
        - lerna.json
        - nx.json
        - turbo.json

        Returns:
            Detected WorkspaceType enum
        """
        if (self.repo_root / "pnpm-workspace.yaml").exists():
            return WorkspaceType.PNPM_WORKSPACE

        # Check package.json for workspaces
        package_json = self.repo_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    if "workspaces" in data:
                        # Determine if npm or yarn based on lockfile
                        if (self.repo_root / "yarn.lock").exists():
                            return WorkspaceType.YARN_WORKSPACE
                        return WorkspaceType.NPM_WORKSPACE
            except Exception:
                pass

        if (self.repo_root / "lerna.json").exists():
            return WorkspaceType.LERNA
        if (self.repo_root / "nx.json").exists():
            return WorkspaceType.NX
        if (self.repo_root / "turbo.json").exists():
            return WorkspaceType.TURBOREPO

        return WorkspaceType.NONE

    def detect_scripts(self) -> dict[str, str]:
        """Extract available scripts from package.json or pyproject.toml.

        Returns scripts in deterministic order (sorted by key).

        Returns:
            Dictionary of script_name → command (sorted by name)
        """
        scripts: dict[str, str] = {}

        # Node.js scripts from package.json
        package_json = self.repo_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    if "scripts" in data and isinstance(data["scripts"], dict):
                        scripts.update(data["scripts"])
            except Exception:
                pass

        # Python scripts from pyproject.toml
        pyproject = self.repo_root / "pyproject.toml"
        if pyproject.exists():
            try:
                with open(pyproject, "rb") as f:
                    data = tomllib.load(f)
                    # Poetry scripts
                    if "tool" in data and "poetry" in data["tool"]:
                        poetry_scripts = data["tool"]["poetry"].get("scripts", {})
                        scripts.update(poetry_scripts)
            except Exception:
                pass

        # Return sorted for determinism
        return dict(sorted(scripts.items()))

    def detect_tooling(self) -> ToolingInfo:
        """Detect presence of common tooling configurations.

        Checks for config files and returns relative paths if found.

        Returns:
            ToolingInfo with paths to detected configs
        """
        typescript: str | None = None
        vitest: str | None = None
        jest: str | None = None
        eslint: str | None = None
        prettier: str | None = None
        pytest: str | None = None
        ruff: str | None = None
        mypy: str | None = None

        # TypeScript
        for ts_config in ["tsconfig.json", "tsconfig.build.json"]:
            if (self.repo_root / ts_config).exists():
                typescript = ts_config
                break

        # Vitest
        for vitest_config_name in [
            "vitest.config.ts",
            "vitest.config.js",
            "vitest.config.mjs",
        ]:
            if (self.repo_root / vitest_config_name).exists():
                vitest = vitest_config_name
                break

        # Jest
        for jest_config_name in [
            "jest.config.js",
            "jest.config.ts",
            "jest.config.json",
        ]:
            if (self.repo_root / jest_config_name).exists():
                jest = jest_config_name
                break

        # ESLint
        for eslint_config_name in [
            ".eslintrc.json",
            ".eslintrc.js",
            ".eslintrc.cjs",
            "eslint.config.js",
        ]:
            if (self.repo_root / eslint_config_name).exists():
                eslint = eslint_config_name
                break

        # Prettier
        for prettier_config_name in [
            ".prettierrc",
            ".prettierrc.json",
            ".prettierrc.js",
            "prettier.config.js",
        ]:
            if (self.repo_root / prettier_config_name).exists():
                prettier = prettier_config_name
                break

        # pytest
        if (self.repo_root / "pytest.ini").exists():
            pytest = "pytest.ini"
        elif (self.repo_root / "pyproject.toml").exists():
            # Check if pyproject.toml has pytest config
            try:
                with open(self.repo_root / "pyproject.toml", "rb") as f:
                    data = tomllib.load(f)
                    if "tool" in data and "pytest" in data["tool"]:
                        pytest = "pyproject.toml"
            except Exception:
                pass

        # Ruff
        if (self.repo_root / "ruff.toml").exists():
            ruff = "ruff.toml"
        elif (self.repo_root / "pyproject.toml").exists():
            try:
                with open(self.repo_root / "pyproject.toml", "rb") as f:
                    data = tomllib.load(f)
                    if "tool" in data and "ruff" in data["tool"]:
                        ruff = "pyproject.toml"
            except Exception:
                pass

        # mypy
        if (self.repo_root / "mypy.ini").exists():
            mypy = "mypy.ini"
        elif (self.repo_root / ".mypy.ini").exists():
            mypy = ".mypy.ini"
        elif (self.repo_root / "pyproject.toml").exists():
            try:
                with open(self.repo_root / "pyproject.toml", "rb") as f:
                    data = tomllib.load(f)
                    if "tool" in data and "mypy" in data["tool"]:
                        mypy = "pyproject.toml"
            except Exception:
                pass

        return ToolingInfo(
            typescript=typescript,
            vitest=vitest,
            jest=jest,
            eslint=eslint,
            prettier=prettier,
            pytest=pytest,
            ruff=ruff,
            mypy=mypy,
        )

    def detect_python_version(self) -> str | None:
        """Extract required Python version from pyproject.toml or setup.py.

        Returns:
            Version string like ">=3.12" or None
        """
        pyproject = self.repo_root / "pyproject.toml"
        if pyproject.exists():
            try:
                with open(pyproject, "rb") as f:
                    data = tomllib.load(f)
                    if "project" in data and "requires-python" in data["project"]:
                        version = data["project"]["requires-python"]
                        if isinstance(version, str):
                            return version
            except Exception:
                pass
        return None

    def detect_node_version(self) -> str | None:
        """Extract required Node version from .nvmrc or package.json engines.

        Returns:
            Version string like "22.12.0" or None
        """
        # Check .nvmrc
        nvmrc = self.repo_root / ".nvmrc"
        if nvmrc.exists():
            try:
                return nvmrc.read_text().strip()
            except Exception:
                pass

        # Check package.json engines
        package_json = self.repo_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    if "engines" in data and "node" in data["engines"]:
                        node_version = data["engines"]["node"]
                        if isinstance(node_version, str):
                            return node_version
            except Exception:
                pass

        return None
