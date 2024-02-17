#!/usr/bin/env python


from hatch_semver.plugin import hooks


def test_hook():
    assert hooks.hatch_register_version_scheme()
