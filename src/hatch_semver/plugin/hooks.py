#!/usr/bin/env python


from hatchling.plugin import hookimpl

from ..semver_scheme import SemverScheme


@hookimpl
def hatch_register_version_scheme():
    return SemverScheme
