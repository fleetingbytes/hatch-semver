#!/usr/bin/env python


from contextlib import nullcontext as no_error
from typing import Generator, Mapping, Optional, Union

import pytest
from _pytest.python_api import RaisesContext
from hatch.utils.fs import Path
from pytest import raises

from hatch_semver.bump_instruction import BumpInstruction as BI
from hatch_semver.errors import ValidationError
from hatch_semver.semver_scheme import SemverScheme

# define some shorthand variables for writing the test parameters
sep = SemverScheme.INSTRUCTION_SEPARATOR.join
bsep = BI.sep.join

val = {"validate-bump": True}
no_val = {"validate-bump": False}

ok = no_error()
not_higher = raises(ValidationError, match="not higher")
not_as_high = raises(ValidationError, match="at least as high")
directly = raises(ValueError, match="directly")
specifically = raises(ValueError, match="specifically")
invalid = raises(ValueError, match="not valid SemVer")


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
        ("build", "2.3.4+build.1", "2.3.4+build.2", val, ok),
        (sep(("minor", "build")), "2.3.4+build.1", "2.4.0+build.1", val, ok),
        ("2.3.4+other-build.1", "2.3.4+build.1", "2.3.4+other-build.1", val, ok),
        ("2.3.4+other-build.1", "2.3.4+build.1", "2.3.4+other-build.1", no_val, ok),
        # custom unnumbered build cannot be bumped
        ("build", "2.3.4+arst", "2.3.4+arst", {}, ok),
        # custom numbered build can be bumped
        ("build", "2.3.4+arst.0", "2.3.4+arst.1", {}, ok),
        ("build", "2.3.4+arst.1", "2.3.4+arst.2", {}, ok),
        ("build", "2.3.4+devdrop0", "2.3.4+devdrop1", {}, ok),
        ("build", "4.3.3-beta.4+custom.3", "4.3.3-beta.4+custom.4", {}, ok),
        ("build", "4.3.3-rc.1", "4.3.3-rc.1+build.1", {}, ok),
        ("build=dev", "2.9.3", "2.9.3+dev.1", val, ok),
        ("dev", "2.9.3", "2.9.3+dev.1", val, ok),
        ("dev=develop", "2.9.3", "2.9.3+develop.1", val, directly),
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
        ("release,beta", "7.1.8-rc.1", "7.1.9-beta.1", val, ok),
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
        ("7.34.2-alpha.1+data.1", "7.34.2-alpha.1", "7.34.2-alpha.1+data.1", {}, ok),
        ("7.34.2-alpha.1+data.1", "7.34.2-alpha.1", "7.34.2-alpha.1+data.1", no_val, ok),
        (bsep(("build", "data")), "7.34.2-alpha.1", "7.34.2-alpha.1+data.1", {}, ok),
        ("3.0.0-almost-done.3", "3.0.0-beta.2", "3.0.0-almost-done.3", {}, not_higher),
        ("3.0.0-almost-done.3", "3.0.0-beta.2+build.1", "3.0.0-almost-done.3", {}, not_higher),
        # change build metadata by entering a specific version
        ("9.1.2-alpha.3+dev.1", "9.1.2-alpha.3+build.1", "9.1.2-alpha.3+dev.1", {}, ok),
        # attempt to bump an alphanumeric identifier (python-semver behavior)
        ("build", "6.3.4-rc.2+verbose", "6.3.4-rc.2+verbose", {}, ok),
        ("build", "6.3.4-rc.2+verbose", "6.3.4-rc.2+verbose", val, ok),
        ("build", "6.3.4-rc.2+verbose", "6.3.4-rc.2+verbose", no_val, ok),
        # multiple instructions
        (sep(("1.0.0", "build")), "1.1.0", "1.0.0+build.1", val, not_as_high),
        (sep(("1.0.0", "build")), "1.1.0", "1.0.0+build.1", {}, not_as_high),
        (sep(("alpha", bsep(("build", "data")))), "7.34.2", "7.34.3-alpha.1+data.1", {}, ok),
        (sep((bsep(("build", "data")), "alpha")), "7.34.2", "7.34.3-alpha.1", {}, ok),
        (sep(("1.0.0", "build")), "1.1.0", "1.0.0+build.1", no_val, ok),
        # temporary precedence violations in intermediate versions
        (sep(("major", "8.0.5")), "8.0.4", "8.0.5", val, ok),
        (sep(("8.0.3", "patch", "build")), "8.0.4", "8.0.4+build.1", val, ok),
        (sep(("8.0.3", "patch", "build")), "8.0.4+build.1", "8.0.4+build.1", val, ok),
        (sep(("8.0.4", "alpha", "pre")), "8.0.4-alpha.1", "8.0.4-alpha.2", val, ok),
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
        ("rc=preview", "3.2.1", "3.2.2-preview.1", {}, ok),
        ("rc", "3.2.1-preview", "3.2.1-preview", {}, not_higher),
        # custom prerelease string once set, cannot be reset,
        # that's a python-semver bug https://github.com/python-semver/python-semver/issues/339
        ("prerelease=beta", "3.2.1-alpha.1", "3.2.1-alpha.2", {}, ok),
        # chained prereleases
        (sep(("patch", "rc")), "1.0.0", "1.0.1-rc.1", {}, ok),
        (sep(("minor", "rc")), "2.3.8", "2.4.0-rc.1", {}, ok),
        (sep(("major", bsep(("rc", "alpha")))), "0.9.5", "1.0.0-alpha.1", {}, ok),
        (sep(("major", "rc", "build")), "0.5.0", "1.0.0-rc.1+build.1", {}, ok),
        (sep(("major", "build", "rc")), "0.5.0", "1.0.0-rc.1", {}, ok),
        (sep(("1.5.0", "rc")), "2.0.0", "1.5.0-rc.1", {}, not_higher),
        (sep(("1.5.0", "rc")), "2.0.0", "1.5.0-rc.1", val, not_higher),
        (sep(("1.5.0", "rc")), "2.0.0", "1.5.0-rc.1", no_val, ok),
        (sep(("2.5.0", "rc")), "2.0.0", "2.5.0-rc.1", {}, ok),
        (sep(("2.5.0+build.1", "rc")), "2.0.0", "2.5.0-rc.1", {}, ok),
        (sep(("2.5.0", "build", "rc")), "2.0.0", "2.5.0-rc.1", {}, ok),
        (sep(("2.5.0", "rc", "build")), "2.0.0", "2.5.0-rc.1+build.1", {}, ok),
        (sep(("minor", "rc", "rc")), "7.0.23", "7.1.0-rc.2", {}, ok),
        (sep(("minor", "rc", "build", "rc")), "7.0.23", "7.1.0-rc.2", {}, ok),
        ("rc", "7.1.0-rc.1+build.1", "7.1.0-rc.2", {}, ok),
        # custom prerelease string once set, cannot be reset,
        # that's a python-semver bug https://github.com/python-semver/python-semver/issues/339
        ("rc=rc", "7.1.0-beta.1+build.1", "7.1.0-beta.2", {}, ok),
        # dev
        ("dev", "3.4.5", "3.4.5+dev.1", {}, ok),
        # custom build string once set, cannot be reset,
        # that's a python-semver bug https://github.com/python-semver/python-semver/issues/339
        (sep(("build", "dev")), "3.4.5", "3.4.5+build.2", {}, ok),
        (sep(("build", "dev", "dev")), "3.4.5", "3.4.5+build.3", {}, ok),
        (sep(("dev", "build=beta")), "3.4.5", "3.4.5+dev.2", {}, ok),
        # malformed specific version
        ("a", "1.0.0", "", {}, invalid),
        # malformed original version
        ("patch", "1.0.0b2", "", {}, invalid),
        # cannot separate with ", "
        (sep(("major", " minor")), "0.4.0", "1.1.0", {}, invalid),
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
