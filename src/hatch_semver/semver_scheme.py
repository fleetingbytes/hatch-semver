#!/usr/bin/env python

from hatchling.version.scheme.plugin.interface import VersionSchemeInterface


class SemverScheme(VersionSchemeInterface):
    """
    Implements the semver versioning scheme for hatch
    See:
    - https://semver.org/
    - https://hatch.pypa.io/latest/plugins/version-scheme/reference/
    """

    PLUGIN_NAME = "semver"

    def update(self, desired_version, original_version, version_data) -> str:
        from semver import VersionInfo

        original = VersionInfo.parse(original_version)
        parts = desired_version.replace("micro", "patch").replace("fix", "patch").split(",")

        for part in parts:
            next_version = getattr(original, "bump_" + part)()
            original = next_version
            if part == "minor":
                next_version = original.bump_minor()
                original = next_version
            elif part in ("post", "rev", "r"):
                raise ValeError(f"Semver has no concept of a post-release. Use 'build' instead")
            elif version == "dev":
                raise ValeError(f"Semver has no concept of a dev-release. Use 'build' instead")
            else:
                if len(parts) > 1:
                    raise ValueError(
                        "Cannot specify multiple update operations with an explicit version"
                    )

                next_version = VersionInfo.parse(part)
                if self.config.get("validate-bump", True) and next_version <= original:
                    raise ValueError(
                        f"Version `{part}` is not higher than the original version `{original_version}`"
                    )
                else:
                    return str(next_version)

        return str(original)
