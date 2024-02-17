#!/usr/bin/env python


import re
from pathlib import Path

import pytest

import hatch_semver.__about__ as about


@pytest.fixture
def changelog_files():
    with (
        open(
            Path(__file__).parent.parent.absolute() / "CHANGELOG.md", encoding="utf-8"
        ) as root_changelog,
        open(
            Path(__file__).parent.parent.absolute() / "docs" / "CHANGELOG.md", encoding="utf-8"
        ) as docs_changelog,
    ):
        yield root_changelog, docs_changelog


semver_re = re.compile(
    r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
)
""" regex adapted from https://semver.org/ (just ditched the start and end of the string)"""


def test_current_version_in_changelog(changelog_files):
    """
    Reads lines from the changelog until it encounters one which starts with
    a heading level 2 (`## `) what should follow is a link to the current version in
    Markdown syntax, e.g. `[1.0.0](https://...)`.
    then it tries to get a match for the semver regex and compares it to the version
    set in __about__.py
    """
    for file in changelog_files:
        found_at_least_one_heading_line = False
        while not (line := file.readline()).startswith("## "):
            continue
        else:
            found_at_least_one_heading_line = True
            match = semver_re.search(line)
            assert match, "Did not find any Semver version in the first level 2 heading"
            version_in_changelog = match.group(0)
            assert (
                version_in_changelog == about.__version__
            ), f"Current version is not at the top of the changelog {file.name}"
        assert found_at_least_one_heading_line, f"Did not find any level 2 heading in {file.name}"
