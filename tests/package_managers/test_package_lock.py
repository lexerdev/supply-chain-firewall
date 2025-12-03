"""
Tests of npm's command line behavior.
"""

import packaging.version as version
import subprocess

"""
Caches the npm installation state before running any tests.
"""


def test_npm_version_output():
    """
    Test that `npm --version` has the required format.
    """
    version_str = subprocess.run(["npm", "--version"], check=True, text=True, capture_output=True)
    version.parse(version_str.stdout.strip())
