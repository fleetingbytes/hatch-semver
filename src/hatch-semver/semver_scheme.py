#!/usr/bin/env python

from hatchling.version.scheme.plugin.interface import VersionSchemeInterface


class SemverScheme(VersionSchemeInterface):
    """
    Implements the semver versioning scheme for hatch
    See:
    - https://semver.org/
    - https://hatch.pypa.io/latest/plugins/version-scheme/reference/
    """
    PLUGIN_NAME = "semver"

    def update(self, desired_version, original_version, version_data) -> str:
        return str("test_version")
