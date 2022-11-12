#!/usr/bin/env python

from hatchling.version.scheme.plugin.interface import VersionSchemeInterface
from typing import Mapping


class SemverScheme(VersionSchemeInterface):
    """
    Implements the semver versioning scheme for hatch
    See:
    - https://semver.org/
    - https://hatch.pypa.io/latest/plugins/version-scheme/reference/
    """

    PLUGIN_NAME = "semver"

    def update(self, desired_version: str, original_version: str, version_data: Mapping) -> str:
        if not desired_version:
            return original_version
        from semver import VersionInfo
        from copy import deepcopy
        from .bump_instruction import BumpInstruction

        original_version = VersionInfo.parse(original_version)
        current_version = deepcopy(original_version)
        instructions: str = desired_version
        for instruction in instructions.split(","):
            bi = BumpInstruction(instruction)
            if bi.version_part == "build":
                current_version = current_version.bump_build(token=bi.token)
            elif bi.version_part == "release":
                current_version = current_version.finalize_version()
            elif bi.is_specific:
                current_version = VersionInfo.parse(bi.version_part)
            else:
                current_version = current_version.next_version(
                    bi.version_part, prerelease_token=bi.token
                )
        if self.config.get("validate-bump", True) and current_version <= original_version:
            raise ValueError(
                f"Version `{current_version}` is not higher than the original version `{original_version}`"
            )
        else:
            return str(current_version)
