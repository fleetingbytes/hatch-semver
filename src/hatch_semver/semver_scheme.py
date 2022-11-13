#!/usr/bin/env python

from hatchling.version.scheme.plugin.interface import VersionSchemeInterface
from typing import Mapping
from semver import VersionInfo
from operator import ge, gt
from copy import deepcopy
from .bump_instruction import BumpInstruction


class SemverScheme(VersionSchemeInterface):
    """
    Implements the semver versioning scheme for hatch
    See:
    - https://semver.org/
    - https://hatch.pypa.io/latest/plugins/version-scheme/reference/
    """

    PLUGIN_NAME = "semver"
    INSTRUCTION_SEPARATOR = ","

    def update(self, desired_version: str, original_version: str, version_data: Mapping) -> str:
        if not desired_version:
            return original_version
        original_version = VersionInfo.parse(original_version)
        current_version = deepcopy(original_version)
        instructions: str = desired_version
        validate = self.config.get("validate-bump", True)
        for instruction in instructions.split(self.INSTRUCTION_SEPARATOR):
            bi = BumpInstruction(instruction)
            last_bump_was_build = False
            if bi.version_part == "build":
                current_version = current_version.bump_build(token=bi.token)
                last_bump_was_build = True
            elif bi.version_part == "release":
                current_version = current_version.finalize_version()
            elif bi.is_specific:
                current_version = VersionInfo.parse(bi.version_part)
            else:
                current_version = current_version.next_version(
                    bi.version_part, prerelease_token=bi.token
                )
        if validate:
            self.validate_bump(current_version, original_version, bumped_build=last_bump_was_build)
        return current_version

    def validate_bump(
        self, current_version: VersionInfo, original_version: VersionInfo, bumped_build: bool
    ) -> None:
        """
        In Semver spec, all builds are equally ranked.
        So for build bumps we validate only whether the current version is equal to the original one.
        For other bumps we validate if the current version is higher than the original.
        """
        if bumped_build:
            comparator = ge
            relation = "at least as high as"
        else:
            comparator = gt
            relation = "higher than"
        if comparator(current_version, original_version):
            return
        else:
            raise ValueError(
                " ".join(
                    (
                        f"Version `{current_version}` is not {relation}",
                        f"the original version `{original_version}`",
                    )
                )
            )
