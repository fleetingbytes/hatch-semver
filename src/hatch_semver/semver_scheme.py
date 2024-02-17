#!/usr/bin/env python

"""
Implements the version scheme interface between hatch and python-semver.
"""

from copy import deepcopy
from operator import ge, gt
from typing import Mapping

from hatchling.version.scheme.plugin.interface import VersionSchemeInterface
from semver import Version

from .bump_instruction import BumpInstruction
from .errors import ValidationError


class SemverScheme(VersionSchemeInterface):
    """
    Implements the semantic version scheme.
    ### References
    - https://semver.org/
    - https://hatch.pypa.io/latest/plugins/version-scheme/reference/
    """

    PLUGIN_NAME = "semver"
    """
    The name of the plugin which is to be used in *pyproject.toml* in [`tool.hatch.version`].
    Value: `semver`
    """
    INSTRUCTION_SEPARATOR = ","
    """
    Separator of bump instructions which the user writes as an argument to `hatch version`.
    Value: `,` (comma)
    """

    def update(self, desired_version: str, original_version: str, version_data: Mapping) -> str:
        """
        Calculates the new version and returns it as a valid semver string.

        If the configuration option [`validate-bump`](https://hatch.pypa.io/latest/plugins/version-scheme/standard/#options) is *True* it calls
                [self.validate_bump](#hatch_semver.semver_scheme.SemverScheme.validate_bump)
                to check if the new version is valid
                as a successor of the original version.

        ### Parameters
        - *desired_version*: A series of commands carrying
                instructions how to bump the current version.
                These commands are separated by `SemverScheme.INSTRUCTION_SEPARATOR`.
                Each such command is in turn parsed and represented as an instance of
                `hatch_semver.bump_instruction.BumpInstruction`.
        - *original_version*: Project's original version. Must be a valid
                semantic version ([regex checker](https://regex101.com/r/Ly7O1x/3/)).
        - *version_data*: Poorly documented argument. Ignored entirely.
                But the plugin's interface requires it. If anyone knows what it
                could be used for, please let me know.

        ### Return
        Returns the new version as a valid semver string.
        """
        if not desired_version:
            return original_version
        original_version = Version.parse(original_version)
        current_version = deepcopy(original_version)
        instructions: str = desired_version
        validate = self.config.get("validate-bump", True)
        rc_bumps_patch = True
        for instruction in instructions.split(self.INSTRUCTION_SEPARATOR):
            bi = BumpInstruction(instruction)
            last_bump_was_build = False
            if bi.version_part == "build":
                current_version = current_version.bump_build(token=bi.token)
                last_bump_was_build = True
            elif bi.version_part == "release":
                current_version = current_version.finalize_version()
                rc_bumps_patch = True
            elif bi.is_specific:
                # Users may enter a specific version string to change nothing but
                # the metadata.
                # This would result in an unnecessary ValidationError if such an instruction
                # comes last in the instruction iterable.
                # To avoid this, we check if nothing but the metadata changed.
                # if so, we will pretend that last_bump_was_build
                temp_old_version = deepcopy(current_version)
                current_version = Version.parse(bi.version_part)
                if temp_old_version == current_version:
                    last_bump_was_build = True
                rc_bumps_patch = False
            else:
                if not rc_bumps_patch and bi.version_part == "prerelease":
                    current_version = current_version.bump_prerelease(token=bi.token)
                    rc_bumps_patch = True
                else:
                    current_version = current_version.next_version(
                        bi.version_part, prerelease_token=bi.token
                    )
                    rc_bumps_patch = False
        if validate:
            self.validate_bump(current_version, original_version, bumped_build=last_bump_was_build)
        return str(current_version)

    def validate_bump(
        self, current_version: Version, original_version: Version, bumped_build: bool
    ) -> None:
        """
        Validates if the current version is a valid successor of the original version.

        ### Parameters
        - *current_version*: the new version which is about to supersede the original version.
        - *original_version*: the original version which is about to be superseded by the new one.
        - *bumped_build*: information whether a bump of the build identifier was performed \
                as the last bump step.

        ### Raises
        Raises [ValidationError](../errors/#validationerror) if the *current_version* (new version) is not higher than the *original_version*. \
        In case only a build identifier bump was performed as the last bump, `ValidationError` is \
        raised if the new version is not at least of equal precedence.
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
            raise ValidationError(
                " ".join(
                    (
                        f"Version `{current_version}` is not {relation}",
                        f"the original version `{original_version}`",
                    )
                )
            )
