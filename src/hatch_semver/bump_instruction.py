#!/usr/bin/env python

from dataclasses import InitVar, dataclass, field
from typing import ClassVar, Optional


@dataclass
class BumpInstruction:
    sep: ClassVar[str] = "="
    acceptable_version_parts: ClassVar[tuple[str]] = (
        "major",
        "minor",
        "patch",
        "prerelease",
        "build",
        "release",
    )
    version_part: str = field(init=False)
    token: Optional[str] = field(init=False)
    is_specific: bool = field(init=False)
    instruction: InitVar[str]

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
