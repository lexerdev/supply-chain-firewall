"""
Defines a package verifier for the NPM package post/preinstall scripts.
"""

import logging
import os
from pathlib import Path

from scfw.constants import SCFW_HOME_VAR
from scfw.ecosystem import ECOSYSTEM
from scfw.package import Package
from scfw.verifier import FindingSeverity, PackageVerifier

_log = logging.getLogger(__name__)


class ScriptVerifier(PackageVerifier):
    """
    A `PackageVerifier` for the NPM package post/preinstall scripts.
    """
    def __init__(self):
        """
        Initialize a new `ScriptVerifier`.
        """

        self.ignored_dependency_ids = set()

    @classmethod
    def name(cls) -> str:
        """
        Return the `ScriptVerifier` name string.

        Returns:
            The class' constant name string: `"ScriptVerifier"`.
        """
        return "ScriptVerifier"

    @classmethod
    def supported_ecosystems(cls) -> set[ECOSYSTEM]:
        """
        Return the set of package ecosystems supported by `ScriptVerifier`.

        Returns:
            The class' constant set of supported ecosystems: `{ECOSYSTEM.Npm}`.
        """
        return {ECOSYSTEM.Npm}

    def verify(self, package: Package) -> list[tuple[FindingSeverity, str]]:
        """
        Query a given package against its preinstall/postinstall scripts.

        Args:
            package: The `Package` to query.

        Returns:
            A list containing any findings for the given package, obtained by looking at the preinstall/postinstall scripts.

        Raises:
            Exception:
                An error occurred while querying a package postinstall or preinstall script.
        """

        if package.ecosystem not in self.supported_ecosystems():
            return [(FindingSeverity.WARNING, f"Package ecosystem {package.ecosystem} is not supported")]

        try:
            # Check if metadata contains scripts (metadata is a tuple of (key, value) pairs)
            if package.metadata is not None:
                for key, value in package.metadata:
                    if key == "scripts" and value:
                        return [
                            (
                                FindingSeverity.WARNING,
                                f"Package {package} contains preinstall/postinstall scripts which may be malicious"
                            )
                        ]
            return []
 

        except Exception as e:
            _log.warning(f"Verification failed for package {package}: {e}")
            return [(FindingSeverity.WARNING, str(e))]


def load_verifier() -> PackageVerifier:
    """
    Export `ScriptVerifier` for discovery by Supply-Chain Firewall.

    Returns:
        An `ScriptVerifier` for use in a run of Supply-Chain Firewall.
    """
    return ScriptVerifier()
