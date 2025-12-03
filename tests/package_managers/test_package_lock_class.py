"""
Tests of `PackageLock`, the `PackageManager` subclass.
"""

import pytest

from scfw.ecosystem import ECOSYSTEM
from scfw.package import Package
from scfw.package_managers.package_lock import PackageLock, MIN_NPM_VERSION

PACKAGE_MANAGER = PackageLock()
"""
Fixed `PackageManager` to use across all tests.
"""

EXPECTED_PACKAGES = [
    ('convert-source-map', '^1.1.0'),
    ('glob', '^7.0.0'),
    ('@babel/cli', '7.6.4'),
    ('slash', '^2.0.0'),
    ('@babel/code-frame', '7.16.7'),
    ('commander', '^2.8.1'),
    ('lodash', '^4.17.13'),
    ('output-file-sync', '^2.0.0'),
    ('@babel/compat-data', '7.17.0'),
    ('fs-readdir-recursive', '^1.1.0'),
    ('source-map', '^0.5.0'),
    ('mkdirp', '^0.5.1'),
    ('@babel/highlight', '^7.16.7'),
    ('@jridgewell/trace-mapping', '^0.3.0'),
    ('@ampproject/remapping', '2.1.2'),
]


def test_npm_list_installed_packages(monkeypatch):
    """
    Test that `Npm.list_installed_packages` correctly parses `npm` output.
    """

    monkeypatch.setattr(
        "scfw.package_managers.package_lock.PACKAGE_LOCK_FILE",
        "tests/package_managers/package-lock.json"
    )

    packages = PACKAGE_MANAGER.list_installed_packages()

    assert len(packages) == len(EXPECTED_PACKAGES)
    
    expected_packages = [
        Package(ecosystem=ECOSYSTEM.Npm, name=name, version=version)
        for name, version in EXPECTED_PACKAGES
    ]
    
    assert set(packages) == set(expected_packages)

    
        
