#!/usr/bin/env python

import datetime

import hatch_semver.__about__ as about


def test_date():
    release_date = about.__release_date__
    assert isinstance(
        release_date, datetime.date
    ), "__release_date__ must be instance of datetime.date"
    today = datetime.datetime.today()
    assert release_date.year == today.year, "date.year in `__about__.py` is not current"
    assert release_date.month == today.month, "date.month in `__about__.py` is not current"
    assert release_date.day == today.day, "date.day in `__about__.py` is not current"


def test_strings():
    for text in (
        about.__author__,
        about.__author_email__,
        about.__maintainer__,
        about.__maintainer_email__,
    ):
        assert text
        assert isinstance(text, str)


def test_emails():
    for mail in (
        about.__author_email__,
        about.__maintainer_email__,
    ):
        assert "@" in mail
