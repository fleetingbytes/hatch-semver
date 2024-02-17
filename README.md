# hatch-semver

A plugin for [hatch][hatch] to support [semantic versioning][semver]. Hatch-semver relies on [python-semver][python-semver] for all the versioning logic.

## Setup

Introduce hatch-semver as a build-dependency to your project (in your `pyproject.toml`):

```toml
[build-system]
requires = [
    "hatchling",
    "hatch-semver",
]
build-backend = "hatchling.build"
```

Further down in `pyproject.toml`, 
where you set up the *hatch version* command, 
set version scheme to `semver`:
```toml
[tool.hatch.version]
path = "src/<your_project>/__about__.py"
validate-bump = true
scheme = "semver"
```

### Beware

Hatch-semver plugin will only work with project versions which can be readily parsed by [python-semver][python-semver].
Therefore, if you are introducing hatch-semver into an existing project, you must **make sure that the project's current version is a valid semantic version.**
You can test that [here][semver-regex].

## Quick Start

Many of hatch's [standard versioning][hatch_versioning] commands also work for hatch-semver to bump your project's version in a semver-compliant way. 
Such command is written as a single string of comma-separated bump instructions as a positional argument of the `hatch version` subcommand, i.e `hatch version <COMMAND>`.

Starting with `0.1.0` as the original version, here is a series of example commands which illustrate some common ways how to bump the version:

| Old Version            | Command             | New Version          |
| ---------------------- | ------------------- | -------------------- |
| `0.1.0`                | `patch`             | `0.1.1`              |
| `0.1.1`                | `minor,patch,patch` | `0.2.2`              |
| `0.2.2`                | `minor`             | `0.3.0`              |
| `0.3.0`                | `rc`                | `0.3.1-rc.1`         |
| `0.3.1-rc.1`           | `rc`                | `0.3.1-rc.2`         |
| `0.3.1-rc.2`           | `release`           | `0.3.1`              |
| `0.3.1`                | `0.9.5`             | `0.9.5`              |
| `0.9.5`                | `major,rc`          | `1.0.0-rc.1`         |
| `1.0.0-rc.1`           | `release`           | `1.0.0`              |

See the [command reference][commands] for all the commands in full detail. If you are familiar with hatch's standard versioning scheme, perhaps a [comparison][comparison] of the standard scheme and hatch-semver will be of interest.


[hatch]: https://hatch.pypa.io/
[hatch_versioning]: https://hatch.pypa.io/latest/version/#updating
[python-semver]: https://github.com/python-semver/python-semver/tree/maint/v2
[semver-regex]: https://regex101.com/r/Ly7O1x/3/
[semver]: https://semver.org/
[commands]: https://fleetingbytes.github.io/hatch-semver/user_guide/1-commands/
[comparison]: https://fleetingbytes.github.io/hatch-semver/user_guide/2-migrating-to-semver/
