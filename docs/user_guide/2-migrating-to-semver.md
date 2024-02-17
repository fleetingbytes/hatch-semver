# Migrating From Hatch Standard Versioning Scheme

If you have used the hatch [standard][hatch_versioning] versioning scheme plugin before and now want to use this semver plugin instead, here is a short rundown of the similarities and differences between the two and their use.


### Identical or Similar Behavior

| Old version | Command   | Standard Plugin     | Semver Plugin      |
| ----------- | --------- | ------------------- | ------------------ |
| `1.0.0`     | `major`   | `2.0.0`             | `2.0.0`            |
| `1.0.0`     | `minor`   | `1.1.0`             | `1.1.0`            |
| `1.0.0`     | `micro`<br>`patch`<br>`fix` | `1.0.1` | `1.0.1`      |
| `1.0.0`     | `dev`     | `1.0.0.dev0`        | `1.0.0+dev.1`      |

### Bumping of Pre-Releases

When bumping only the pre-release segment of a version which has not yet any pre-release segment, hatch-semver automatically bumps the patch version.
It also automatically adds a purely numeric identifier *1* through which bumping becomes possible. Without a numeric identifier, this pre-release [could not be bumped][unbumpable].

| Old version | Command   | Standard Plugin     | Semver Plugin      | Comment                    |
| ----------- | -------   | ------------------- | ------------------ | -------------------------- |
| `1.0.0`     | `alpha`   | `1.0.0a0`           | `1.0.1-alpha.1`    | patch version auto-bumped  |
| `1.0.0`     | `beta`    | `1.1.0b0`           | `1.0.1-beta.1`     | patch version auto-bumped  |
| `1.0.0`     | `rc`      | `1.1.0rc0`          | `1.0.1-rc.1`       | patch version auto-bumped  |

The patch segment of the [version core][bnf] is not bumped, if pre-release is bumped in a [chained command][chain] where a version core bump has occurred before. 

| Old version | Command        | Standard Plugin | Semver Plugin   | Comment                        |
| ----------- | -------------- | ----------------| --------------- | ------------------------------ |
| `1.0.0`     | `patch,alpha`  | `1.0.1a0`       | `1.0.1-alpha.1` | patch version not auto-bumped  |
| `1.0.0`     | `minor,beta`   | `1.1.0b0`       | `1.1.0-beta.1`  | patch version not auto-bumped  |
| `1.0.0`     | `major,rc`     | `2.0.0rc0`      | `2.0.0-rc.1`    | patch version not auto-bumped  |

See more [examples][chained-pre] in the commands documentation.

### Differences

The `release` command of hatch-semver does not simply return the [version core][bnf] stripped off the pre-release and build idetifiers.
It performs a real bump *to the release version*. 
This normally goes along with a [validation][validation] check. 
When you try to release version which is not a prerelease, this will raise a ValidationError.

| Old version   | Command   | validate-bump | Standard Plugin     | Semver Plugin      |
| ------------- | --------- | ------------- | ------------------- | ------------------ |
| `1.0.0`       | `release` | True          | `1.0.0`             | `ValidationError`  |
| `1.0.0`       | `release` | False         | `1.0.0`             | `1.0.0`            |
| `1.0.0+dev.1` | `release` | True          | `1.0.0`             | `ValidationError`  |
| `1.0.0+dev.1` | `release` | False         | `1.0.0`             | `1.0.0`            |

### Unsupported Commands

Hatch's [standard][hatch_versioning]'s versioning scheme's `rev`, `r`, `post` commands are not supported. 
There is no concept of a revision or a post-release in [Semver][semver]. 
However, with `build=post`, for instance you could add the build identifiers *post* and *1* which would be similar to a PEP 440 post-release.
Like in PEP 440, also in Semver build identifiers have the same precedence.

The abbreviations `a`, `b`, and `c` for `alpha`, `beta`, `rc`, and `preview`, respectively, are also not supported and will result in [python-semver][python-semver] throwing a `ValueError` with *... is not a valid SemVer string*. Hatch-semver actually uses `pre` as an alias for [pre-release][prerelease].

Semver allows custom identifiers in prereleases, so if you really wanted an `a0` pre-release, you could achieve it by bumping to a specific version, i.e. `hatch version 1.2.3-a0` although such alphanumeric identifiers [cannot be bumped][unbumpable] by [python-semver].
Better go with `1.2.3-a.1` which could be bumped to `1.2.3-a.2`, `1.2.3-a.3` etc.


[hatch_versioning]: https://hatch.pypa.io/latest/version/#updating
[python-semver]: https://github.com/python-semver/python-semver
[semver]: https://semver.org/
[validation]: https://hatch.pypa.io/latest/plugins/version-scheme/standard/#options
[unbumpable]: ../1-commands/#alphanumeric-pre-release-identifiers
[bnf]: https://semver.org/#backusnaur-form-grammar-for-valid-semver-versions
[chain]: ../1-commands/#chained-commands
[chained-pre]: ../1-commands/#chained-with-a-version-core-bump
[prerelease]: ../1-commands/#pre-release
