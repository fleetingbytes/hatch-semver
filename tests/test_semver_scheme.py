#!/usr/bin/env python


import pytest
from hatch_semver.semver_scheme import SemverScheme
from dataclasses import dataclass
from typing import Mapping, Optional


@dataclass
class AbstractTestCase:
    comment: str
    version_settings: Mapping[str, bool]
    desired: str
    original: str


@dataclass
class NormalTestCase(AbstractTestCase):
    expected: str


@dataclass
class ErrorTestCase(AbstractTestCase):
    err_type: Exception
    match: str


testcases = (
    NormalTestCase(
        comment="set specific version",
        version_settings={},
        desired="9000.0.0-rc.1",
        original="1.0.0",
        expected="9000.0.0-rc.1",
    ),
    NormalTestCase(
        comment="set specific version when it is allowed to desire not higher version",
        version_settings={"validate-bump": False},
        desired="0.24.4",
        original="1.0.0-dev.0",
        expected="0.24.4",
    ),
    NormalTestCase(
        comment="release",
        version_settings={},
        desired="release",
        original="9000.0.0-rc.1+dev5",
        expected="9000.0.0",
    ),
    NormalTestCase(
        comment="major",
        version_settings={},
        desired="major",
        original="9000.0.0-rc.1+dev5",
        expected="9001.0.0",
    ),
    NormalTestCase(
        comment="minor",
        version_settings={},
        desired="minor",
        original="9000.0.0-rc.1+dev5",
        expected="9000.1.0",
    ),
)


error_testcases = (
    ErrorTestCase(
        comment="desiring to change to a non-semver-compliant version string",
        version_settings={},
        desired="1.0",
        original="0.1.0",
        err_type=ValueError,
        match="1.0 is not valid SemVer string",
    ),
    ErrorTestCase(
        comment="original version is not non-semver-compliant",
        version_settings={},
        desired="0.1.0",
        original="1.0",
        err_type=ValueError,
        match="1.0 is not valid SemVer string",
    ),
)


def test_errors(isolation):
    for etc in error_testcases:
        scheme = SemverScheme(str(isolation), etc.version_settings)
        with pytest.raises(etc.err_type, match=etc.match):
            scheme.update(etc.desired, etc.original, {})


def test_normal(isolation):
    for tc in testcases:
        scheme = SemverScheme(str(isolation), tc.version_settings)
        assert scheme.update(tc.desired, tc.original, {}) == tc.expected, tc.comment
