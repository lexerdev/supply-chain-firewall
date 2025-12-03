"""
Tests of `ScriptVerifier`.
"""

import pytest

from scfw.ecosystem import ECOSYSTEM
from scfw.package import Package
from scfw.verifier import FindingSeverity
from scfw.verifiers import FirewallVerifiers
from scfw.verifiers.script_verifier import ScriptVerifier

# Create a single ScriptVerifier to use for testing
SCRIPT_VERIFIER = ScriptVerifier()

# Test set for NPM packages with scripts
# Format: (name, version, has_warning)
# has_warning=True means package has preinstall/postinstall scripts
NPM_TEST_SET = [
    ("package-with-preinstall", "1.0.0", True),
    ("package-with-postinstall", "2.0.0", True),
    ("package-with-both-scripts", "3.0.0", True),
    ("safe-package-no-scripts", "1.0.0", False),
    ("package-with-other-scripts-only", "1.0.0", False),
]


def test_script_verifier_with_scripts():
    """
    Run a test of the `ScriptVerifier` against packages with scripts.
    """
    # Create test packages
    test_set = []
    for name, version, has_scripts in NPM_TEST_SET:
        if has_scripts:
            # metadata is a tuple of (key, value) pairs
            # For scripts, we use a simple truthy value instead of a dict
            metadata = (("scripts", "preinstall: node install.js"),)
        else:
            metadata = ()
        package = Package(ECOSYSTEM.Npm, name, version, metadata)
        test_set.append((package, has_scripts))

    # Create a modified `FirewallVerifiers` only containing the Script verifier
    verifier = FirewallVerifiers(ECOSYSTEM.Npm)
    verifier._verifiers = [SCRIPT_VERIFIER]

    reports = verifier.verify_packages([test[0] for test in test_set])
    warning_report = reports.get(FindingSeverity.WARNING)
    critical_report = reports.get(FindingSeverity.CRITICAL)

    # ScriptVerifier should not produce critical findings
    assert not critical_report

    for package, has_warning in test_set:
        if has_warning:
            assert (warning_report and warning_report.get(package))
        else:
            assert (not (warning_report and warning_report.get(package)))
