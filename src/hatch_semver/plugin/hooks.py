#!/usr/bin/env python


from hatchling.plugin import hookimpl

from ..semver_scheme import SemverScheme

"""
The registration hook for [hatch](https://github.com/pypa/hatch/tree/master/backend/src/hatchling/plugin)
"""


@hookimpl
def hatch_register_version_scheme():
    """
    Returns `hatch_semver.semver_scheme.SemverScheme`.
    By this our plugin can be somehow registered in [hatch](https://hatch.pypa.io/).
    """
    return SemverScheme
