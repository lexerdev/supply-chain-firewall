"""
Provides a `PackageManager` representation of `package-lock.json`.
"""

import json
import subprocess
from typing import Optional

from packaging.version import InvalidVersion, Version, parse as version_parse

from scfw.ecosystem import ECOSYSTEM
from scfw.package import Package
from scfw.package_manager import PackageManager, UnsupportedVersionError

MIN_NPM_VERSION = version_parse("7.0.0")

NODE_MODULES_PREFIX = "node_modules/"
PACKAGE_LOCK_FILE = "package-lock.json"
NPM_EXECUTABLE = "npm"

class PackageLock(PackageManager):
    
    def __init__(self, executable: Optional[str] = NPM_EXECUTABLE):
        self._executable = executable

    @classmethod
    def name(cls) -> str:
        """
        Return the token for invoking `package-lock` on the command line.
        """
        return "package-lock"

    @classmethod
    def ecosystem(cls) -> ECOSYSTEM:
        """
        Return the ecosystem of packages managed by `package-lock.json`.
        """
        return ECOSYSTEM.Npm
    
    def executable(self) -> str:
        return self._executable
    
    def resolve_install_targets(self, command: list[str]) -> list[Package]:
        pass
    
    def run_command(self, command: list[str]) -> int:
        pass

    def list_installed_packages(self) -> list[Package]:
        """
        List all `npm` packages installed in the `package-lock.json` file.

        Returns:
            A `list[Package]` representing all `npm` packages installed in the `package-lock.json` file.

        Raises:
            RuntimeError: Failed to list installed packages or decode report JSON.
            ValueError: Encountered a malformed report for an installed package.
            UnsupportedVersionError: The underlying `npm` executable is of an unsupported version.
        """
        def remove_prefix(s: str) -> str:
            w = s.split(NODE_MODULES_PREFIX)
            return w[-1] if len(w) > 1 else s

        def dependencies_to_packages(dependencies: dict[str, dict]) -> set[Package]:
            packages = set()

            for name, package_data in dependencies.items():
                if name == "":  # Skip the root package entry
                    continue
                if not isinstance(package_data, str) and (package_dependencies := package_data.get("dependencies")):
                    packages |= dependencies_to_packages(package_dependencies)
                packages.add(Package(ECOSYSTEM.Npm, remove_prefix(name), package_data if isinstance(package_data, str) else package_data.get("version")))

            return packages

        self._check_version()

        try:
            with open(PACKAGE_LOCK_FILE, 'r', encoding='utf-8') as lockfile:
                dependencies = json.loads(lockfile.read().strip())["packages"]
                return list(dependencies_to_packages(dependencies)) if dependencies else []

        except json.JSONDecodeError:
            raise RuntimeError("Failed to decode installed package report JSON")
        
        except FileNotFoundError:
            raise RuntimeError(f"Failed to read npm lockfile at 'package-lock.json'")
        
        except KeyError:
            raise ValueError("Malformed installed package report")
        

    def _check_version(self):
        """
        Check whether the underlying `npm` executable is of a supported version.

        Raises:
            UnsupportedVersionError: The underlying `npm` executable is of an unsupported version.
        """
        def get_npm_version(executable: str) -> Optional[Version]:
            try:
                # All supported versions adhere to this format
                npm_version = subprocess.run([executable, "--version"], check=True, text=True, capture_output=True)
                return version_parse(npm_version.stdout.strip())
            except InvalidVersion:
                return None

        npm_version = get_npm_version(self._executable)
        if not npm_version or npm_version < MIN_NPM_VERSION:
            raise UnsupportedVersionError(f"npm before v{MIN_NPM_VERSION} is not supported")
