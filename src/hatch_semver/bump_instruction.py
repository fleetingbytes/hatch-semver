#!/usr/bin/env python

from dataclasses import InitVar, dataclass, field
from typing import ClassVar, Optional


@dataclass
class BumpInstruction:
    """
    A dataclass for representing a single instruction from the
    chain of bump instructions (i.e. a part of the *desired_version*
    argument of `hatch_semver.semver_scheme.SemverScheme.update`.

    Takes a single string as an argument and calculates the values
    of an instance's attributes.
    """

    sep: ClassVar[str] = "="
    """
    Value: `=`.
    Separator of the version segment's name and the value of its identifier.
    Used to set a custom prerelease identifier, e.g. `prerelease=beta`
    or a custom build identifier, e.g. `build=develop`.
    """
    acceptable_version_parts: ClassVar[tuple[str]] = (
        "major",
        "minor",
        "patch",
        "prerelease",
        "build",
        "release",
    )
    """
    Used to decide whether the user wants to set a specific version or not
    (see [is_specific](#hatch_semver.bump_instruction.BumpInstruction.is_specific))
    If only a relative bump is requested, the bump instruction (which contains
    the name of the version part to bump) would correspond to one of the strings in
    this tuple. If not, then we assume that the string given in
    [version_part](#hatch_semver.bump_instruction.BumpInstruction.version_part)
    is a specific version.
    """
    version_part: str = field(init=False)
    """
    Is either one of the
    [acceptable_version_parts](#hatch_semver.bump_instruction.BumpInstruction.acceptable_version_parts)
    or one of their aliases. Can also hold the value of the a specific version
    if the user wants to set it that way.
    """
    token: Optional[str] = field(init=False)
    """
    Holds the value of a custom identifier, e.g. `beta`, or `develop`.
    """
    is_specific: bool = field(init=False)
    """
    Information whether the user intends to set a specific version value,
    rather than bump any of the version segments.
    """
    instruction: InitVar[str]
    """
    Only available in the init phase of the instance. This is the raw
    unparsed bump instruction. One part of the string given to
    `hatch_semver.semver_scheme.SemverScheme.update`
    as the *desired_version* argument.
    """

    def __post_init__(self, instruction) -> None:
        if self.sep not in instruction:
            raw_version_part = instruction
            raw_token = None
        else:
            raw_version_part, raw_token = instruction.split(self.sep, maxsplit=1)
        self.version_part, self.token, self.is_specific = self.normalize_version_part(
            raw_version_part, raw_token
        )

    @classmethod
    def normalize_version_part(cls, part: str, token: str) -> tuple[str, str, bool]:
        """
        Effectively parses the raw string of the bump instruction into a tuple
        of atomic values which it returns. The `BumpInstruction.__post_init__`
        then assigns them to the instance's attributes.

        Version parts (version segments) can be referred to by many names.
        For instance the *patch* segment can be called *micro* or *fix*,
        the *pre-release* segment *pre*, *rc*, etc.

        This method normalizes all aliases to their native name
        (see [acceptable_version_parts](#hatch_semver.bump_instruction.BumpInstruction.acceptable_version_parts).
        It also handles shortcuts like `alpha` or `dev` which are actually
        `prerelease=alpha` or `build=dev` in their full syntax, i.e. they
        are to be understood as a version part with a custom identifier.

        ### Parameters
        - *cls*: the `BumpInstruction` class.
        - *part*: version part (`major`, `minor`, ...), alias (`rc`, `fix`, ...),
                a shortcut (`alpha`, `dev`, ...), or a specific version (e.g. `3.4.5`)
        - *token*: a custom token. If the user has specified something like `prerelease=alpha`,
                `alpha` would be the token (what the pre-release identifier should be called).

        ### Return
        a tuple of:

        - *part*: normalized to the native names defined in
                [acceptable_version_parts](#hatch_semver.bump_instruction.BumpInstruction.acceptable_version_parts), or a specific version
        - *token*: whatever the identifier's value should be
        - *specific*: information whether *part* contains a specific version,
                rather than a version part
        """
        if part in ("pre", "prerelease", "pre-release", "rc"):
            part = "prerelease"
        elif part in ("micro", "fix"):
            part = "patch"
        elif part in ("alpha", "beta"):
            if token:
                raise ValueError(
                    " ".join(
                        (
                            f"{part} version cannot be set to {token} directly.",
                            f"Use 'prerelease={part}' instead",
                        )
                    )
                )
            token = part
            part = "prerelease"
        elif part in ("dev",):
            if token:
                raise ValueError(
                    f"{part} version cannot be set to {token} directly. Use 'build={part}' instead"
                )
            token = part
            part = "build"
        if token:
            if part in ("major", "minor", "patch", "release"):
                raise ValueError(
                    f"{part} version cannot be set to {token} specifically. Use {part} alone"
                )
        if part in cls.acceptable_version_parts:
            specific = False
        else:
            specific = True
        return part, token, specific
