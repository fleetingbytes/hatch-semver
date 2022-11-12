#!/usr/bin/env python


from hatch_semver.bump_instruction import BumpInstruction as BI
import pytest
from typing import Optional


class TestInvalidToken:
    @pytest.mark.parametrize("part, token", (("alpha", "3"), ("beta", "2")))
    def test_invalid_prerelease_token(self, part: str, token: str) -> None:
        with pytest.raises(
            ValueError,
            match=f"{part} version cannot be set to {token} directly. Use 'prerelease={part}' instead",
        ):
            BI(f"{part}={token}")

    @pytest.mark.parametrize("part, token", (("dev", "3"),))
    def test_invalid_build_token(self, part: str, token: str) -> None:
        with pytest.raises(
            ValueError,
            match=f"{part} version cannot be set to {token} directly. Use 'build={part}' instead",
        ):
            BI(f"{part}={token}")

    @pytest.mark.parametrize(
        "part, norm_part, token",
        (
            ("major", "major", "3"),
            ("minor", "minor", "2"),
            ("patch", "patch", "4"),
            ("fix", "patch", "5"),
            ("micro", "patch", "6"),
            ("release", "release", "7"),
        ),
    )
    def test_invalid_part_token(self, part: str, norm_part: str, token: str) -> None:
        with pytest.raises(
            ValueError,
            match=f"{norm_part} version cannot be set to {token} specifically. Use {norm_part} alone",
        ):
            BI(f"{part}={token}")


class TestSeparatorNotInInstruction:
    @pytest.mark.parametrize(
        "instruction, part, token, specific",
        (
            ("", "", None, True),
            ("something-specific", "something-specific", None, True),
            ("release", "release", None, False),
            ("major", "major", None, False),
            ("minor", "minor", None, False),
            ("patch", "patch", None, False),
            ("fix", "patch", None, False),
            ("micro", "patch", None, False),
            ("pre", "prerelease", None, False),
            ("prerelease", "prerelease", None, False),
            ("pre-release", "prerelease", None, False),
            ("rc", "prerelease", None, False),
            ("build", "build", None, False),
            ("alpha", "prerelease", "alpha", False),
            ("beta", "prerelease", "beta", False),
            ("dev", "build", "dev", False),
        ),
    )
    def test_no_separator(
        self, instruction: str, part: str, token: Optional[str], specific: bool
    ) -> None:
        bi = BI(instruction)
        assert bi.version_part == part
        if token is None:
            assert bi.token is None
        else:
            assert bi.token == token
        assert bi.is_specific == specific


class TestSeparator:
    @pytest.mark.parametrize("instruction", ("pre=neat"))
    def test_maxsplit(self, instruction: str) -> None:
        breakpoint()
        bi = BI(instruction)
        assert bi.token.count(BI.sep) == instruction.count(BI.sep) - 1
