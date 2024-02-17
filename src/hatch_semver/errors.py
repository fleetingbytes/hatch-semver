#!/usr/bin/env python


"""
Hatch-semver's own error types
"""


class HatchSemverError(Exception):
    """
    Base class for all hatch-semver errors.
    """

    pass


class ValidationError(HatchSemverError):
    """
    Raised if the new version is not a valid successor of the original version.
    """

    pass
