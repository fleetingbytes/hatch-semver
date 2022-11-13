#!/usr/bin/env python


import pytest
from pytest import raises
from hatch_semver.semver_scheme import SemverScheme
from hatch.utils.fs import Path
from typing import Optional, Generator, Mapping, Union
from hatch_semver.bump_instruction import BumpInstruction as BI
from contextlib import nullcontext as no_error
from _pytest.python_api import RaisesContext

# define some shorthand variables for writing the test parameters
sep = SemverScheme.INSTRUCTION_SEPARATOR.join
bsep = BI.sep.join

val = {"validate-bump": True}
no_val = {"validate-bump": False}

ok = no_error()
not_higher = raises(ValueError, match="not higher")
not_as_high = raises(ValueError, match="at least as high")
directly = raises(ValueError, match="directly")
specifically = raises(ValueError, match="specifically")

@pytest.mark.parametrize(
    "instructions, original, expected, settings, exp_error",
    (
        # no instructions, just give us the current version
        ("", "0.0.1", "0.0.1", val, ok),
        ("", "0.0.1", "0.0.1", no_val, ok),
        ("", "0.0.1", "0.0.1", {}, ok),
        (None, "0.1.0", "0.1.0", val, ok),
        (None, "0.1.0", "0.1.0", no_val, ok),
        (None, "0.1.0", "0.1.0", {}, ok),
        # bump build
        ("build", "2.3.4", "2.3.4+build.1", val, ok),
        ("build", "2.3.4+build.1", "2.3.4+build.2", no_val, ok),
        ("build", "2.3.4+arst", "2.3.4+arst.2", {}, ok),
        ("build", "2.3.4+devdrop0", "2.3.4+devdrop0.2", {}, ok),
        ("build", "4.3.3-beta.4+custom.3", "4.3.3-beta.4+custom.4", {}, ok),
        # bump to release
        ("release", "2.3.4-beta.3+devdrop0", "2.3.4", {}, ok),
        ("release", "2.3.4-beta.3+devdrop0", "2.3.4", val, ok),
        ("release", "2.3.4-beta.3+devdrop0", "2.3.4", no_val, ok),
        ("release", "12.35.49-rc.3", "12.35.49", {}, ok),
        ("release", "6.4.2-custom-pre-release", "6.4.2", {}, ok),
        ("release", "6.4.2-custom-pre-release", "6.4.2", val, ok),
        ("release", "6.4.2-custom-pre-release", "6.4.2", no_val, ok),
        ("release", "12.35.49+build.3", "12.35.49", no_val, ok),
        ("release", "5.2.3", "5.2.3", no_val, ok),
        ("release", "2.3.4", "2.3.4", {}, not_higher),
        ("release", "2.3.4", "2.3.4", val, not_higher),
        ("release", "12.35.49+build.3", "12.35.49", val, not_higher),
        # specific version
        ("3.21.7-gamma+didaktik", "1.0.1", "3.21.7-gamma+didaktik", {}, ok),
        ("3.21.7-gamma+didaktik", "1.0.1", "3.21.7-gamma+didaktik", val, ok),
        ("3.21.7-gamma+didaktik", "1.0.1", "3.21.7-gamma+didaktik", no_val, ok),
        ("3.21.7-gamma+didaktik", "3.21.7-gandalf", "3.21.7-gamma+didaktik", {}, not_higher),
        ("3.21.7-gamma+didaktik", "3.21.7-gandalf", "3.21.7-gamma+didaktik", val, not_higher),
        ("3.21.7-gamma+didaktik", "3.21.7-gandalf", "3.21.7-gamma+didaktik", no_val, ok),
        ("7.34.2-alpha+data", "7.34.2-alpha.1", "7.34.2-alpha+data", {}, not_higher),
        ("7.34.2-alpha.1+data.1", "7.34.2-alpha.2", "7.34.2-alpha.1+data.1", {}, not_higher),
        ("7.34.3-alpha.1+data.1", "7.34.2", "7.34.3-alpha.1+data.1", {}, ok),
        ("7.34.2-alpha.1+data.1", "7.34.2-alpha.1", "7.34.2-alpha.1+data.1", {}, not_higher),
        ("7.34.2-alpha.1+data.1", "7.34.2-alpha.1", "7.34.2-alpha.1+data.1", no_val, ok),
        (bsep(("build", "data")), "7.34.2-alpha.1", "7.34.2-alpha.1+data.1", {}, ok),
        # multiple instructions
        (sep(("1.0.0", "build")), "1.1.0", "1.0.0+build.1", val, not_as_high),
        (sep(("1.0.0", "build")), "1.1.0", "1.0.0+build.1", {}, not_as_high),
        (sep(("alpha", bsep(("build", "data")))), "7.34.2", "7.34.3-alpha.1+data.1", {}, ok),
        (sep((bsep(("build", "data")), "alpha")), "7.34.2", "7.34.3-alpha.1", {}, ok),
        (sep(("1.0.0", "build")), "1.1.0", "1.0.0+build.1", no_val, ok),
        # questionable custom value
        (bsep(("build", "build.1")), "9.8.4", "9.8.4+build.1.1", {}, ok),
        # wrong custom values
        (bsep(("alpha", "myalpha")), "1.3.5", "", {}, directly),
        (bsep(("beta", "mybeta")), "1.3.5", "", val, directly),
        (bsep(("minor", "4")), "1.3.5", "", no_val, specifically),
        # release candidates
        ("rc", "4.2.1", "4.2.2-rc.1", {}, ok),
        ("pre", "4.2.1", "4.2.2-rc.1", {}, ok),
        ("prerelease", "4.2.1", "4.2.2-rc.1", {}, ok),
        ("pre-release", "4.2.1", "4.2.2-rc.1", {}, ok),
        (bsep(("rc", "myrc")), "1.3.5", "1.3.6-myrc.1", val, ok),
        (sep(("rc", "rc", "rc", "rc")), "6.4.3", "6.4.4-rc.4", {}, ok),
        # prereleases
        ("alpha", "1.0.0+dev", "1.0.1-alpha.1", {}, ok),
        ("beta", "1.0.0+dev", "1.0.1-beta.1", {}, ok),
        (bsep(("pre", "gamma")), "1.0.0+dev", "1.0.1-gamma.1", {}, ok),
        # dev
        ("dev", "3.4.5","3.4.5+dev.1", {}, ok),
        (bsep(("build", "dev")), "3.4.5","3.4.5+dev.1", {}, ok),
    ),
)
def test_semver_scheme(
    isolation: Generator[Path, None, None],
    instructions: Optional[str],
    original: str,
    expected: str,
    settings: Mapping[str, bool],
    exp_error: Union[no_error, RaisesContext],
) -> None:
    scheme = SemverScheme(str(isolation), settings)
    with exp_error:
        assert scheme.update(instructions, original, {}) == expected
