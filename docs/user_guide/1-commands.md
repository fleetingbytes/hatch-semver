# Commands

A hatch-semver command is written as a single string of comma-separated bump instructions as the single positional argument of the `hatch version` subcommand, i.e `hatch version <COMMAND>`.


## No Command At All

If no command is given, `hatch version` will simply return the current version of the project.

## Specific Version

You can set a specific version directly, as long as it is a [semantic version][semver-regex]. If [bump validation][validation] is used, the resulting version must also be higher, or—if only the build identifier changes—at least equal in precedence.

| Old Version            | Command             | validate-bump | New Version          |
| ---------------------- | ------------------- | ------------- | -------------------- |
| `2.3.4`                | `13.5.26`           | True          | `13.5.26`            |
| `2.3.4`                | `2.3.3`             | True          | ValidationError      |
| `2.3.4`                | `2.3.3`             | False         | `2.3.3`              |
| `2.3.4`                | `2.3.4-alpha`       | True          | ValidationError      |
| `2.3.4`                | `2.3.4-alpha`       | False         | `2.3.4-alpha`        |
| `2.3.4-alpha`          | `2.3.4`             | True          | `2.3.4`              |
| `3.0.0-beta.2`         | `3.0.0-almost-done.3` | True        | ValidationError      |
| `3.0.0-beta.2`         | `3.0.0-rc.1`        | True          | `3.0.0-rc.1`         |
| `4.3.2-rc.2+zoom`      | `4.3.2-rc.2+dev`    | True          | `4.3.2-rc.2+dev`     |

Keep in mind that all pre-releases are ranked by their ASCII sort order and all of them are lower in precedence than the associated normal version, hence the validation errors.
Build versions have all the same precedence, hence no validation error.

## Major, Minor, Patch

| Old Version            | Command             | New Version          |
| ---------------------- | ------------------- | -------------------- |
| `0.1.0`                | `patch`<br>`fix`<br>`micro` | `0.1.1`      |
| `0.1.1`                | `minor`             | `0.2.0`              |
| `1.0.0`                | `major`             | `1.0.0`              |

These commands bump the [version core][bnf]. `fix` and `micro` are aliases of `patch`.

[Pre-release][pre] and [build][build] commands allow specifying their value with `=`.
This, however, is not possible for the version core bump commands. 
To accomplish bigger version bumps, they can be [chained][chained-commands] [together][chained-pre] or replaced by a [specific version][specific-version].

| Old Version            | Command             | New Version          |
| ---------------------- | ------------------- | -------------------- |
| `0.1.0`                | `major=7,minor=27`  | ValueError           |
| `0.1.0`                | `7.27.6`            | `7.27.6`             |
| `0.1.0`                | `fix,fix,fix,fix`   | `0.1.4`              |
| `0.1.0`                | `major,major,minor` | `2.1.0`              |

## Pre-Release

If applied on a version without [pre-release identifiers][bnf], `prerelease`—or its aliases `rc`, `pre`, `pre-release`—**will bump the patch version** and introduce the default pre-release identifiers *rc* and *1*.
If some pre-release identifiers are already present and the last one is a number, it will be bumped. Naturally, this drops any present build identifiers.

| Old Version            | Command             | New Version          |
| ---------------------- | ------------------- | -------------------- |
| `0.9.5`                | `prerelease`<br>`rc`<br>`pre`<br>`pre-release` | `0.9.6-rc.1` |
| `0.9.5-rc.1`           | `pre`               | `0.9.5-rc.2`         |
| `0.9.5-rc.2+debug`     | `rc`                | `0.9.5-rc.3`         |
| `0.9.5+dev.3`          | `rc`                | `0.9.6-rc.1`         |

### Chained With a Version Core Bump

You can [chain][chained-commands] multiple commands together. 
If the [version core][bnf] is bumped before the pre-release bump, the pre-release bump **will not bump the patch version**.

| Old Version            | Command             | New Version          |
| ---------------------- | ------------------- | -------------------- |
| `0.8.6`                | `rc`                | `0.8.7-rc.1`         |
| `0.8.6`                | `patch,rc`          | `0.8.7-rc.1`         |
| `0.8.6`                | `minor,rc`          | `0.9.0-rc.1`         |
| `0.8.6`                | `major,rc`          | `1.0.0-rc.1`         |
| `0.8.6`                | `1.3.5,rc,rc`       | `1.3.5-rc.2`         |
| `0.8.6`                | `major,rc,build`    | `1.0.0-rc.1+build.1` |
| `0.8.6`                | `major,build,rc`    | `1.0.0-rc.1`         |

### Alphanumeric Pre-Release Identifiers

If pre-release identifiers are present but the last one is an [alphanumeric identifier][bnf]—i.e. not a number—it **will not be bumped** and no further identifiers are introduced (current [python-semver][python-semver] behavior<sup>[issue][issue]</sup>). 
This will normally result in a `ValidationError`, unless you have turned off [validate-bump][validation] in your hatch version settings.

| Old Version            | Command             | validate-bump | New Version          |
| ---------------------- | ------------------- | ------------- | -------------------- |
| `0.9.7-rc1`            | `prerelease`        | True          | ValidationError      |
| `0.9.7-rc1`            | `prerelease`        | False         | `0.9.7-rc1`          |

### Custom Identifiers

You can define your own pre-release identifier like this: `prerelease=<identifier>`:

| Old Version            | Command              | New Version          |
| ---------------------- | -------------------- | -------------------- |
| `0.3.3`                | `pre=alpha`          | `0.3.4-alpha.1`      |
| `0.3.4-alpha.1`        | `pre`                | `0.3.4-alpha.2`      |
| `0.3.4-alpha.2`        | `pre=beta`           | `0.3.4-alpha.3` <sup>[bug][bug]</sup> |

Unfortunately, once a pre-release identifier has been introduced, it cannot be changed later. This is a current [python-semver bug][bug].
For now you can work around it by using a [specific version][specific-version] command. 
Bumping the version core will effectively  also drop the identifier, so then another identifier can be introduced again.

### Alpha, Beta Shortcuts

`alpha` and `beta` are very common pre-release identifiers.
Hatch-semver provides the `alpha` and `beta` shortcuts for `prerelease=alpha` and `prerelease=beta`, respectively.

| Old Version            | Command              | New Version          |
| ---------------------- | -------------------- | -------------------- |
| `5.12.3`               | `alpha`              | `5.12.4-alpha.1`     |
| `5.12.3`               | `beta`               | `5.12.4-beta.1`      |

`alpha` and `beta` themselves are not *aliases* of `prerelease`.
You cannot use them to define a custom identifier.
`rc`, however, *is* a true alias and allows this.

| Old Version            | Command              | New Version          |
| ---------------------- | -------------------- | -------------------- |
| `5.12.3`               | `alpha=ALPHA`        | ValueError           |
| `5.12.3`               | `rc=RC`              | `5.12.4-RC.1`        |

## Release

The `release` command turns a pre-release version into a final release.
If applied on a bare [version core][bnf], it will result in a ValidationError because the resulting version is not higher than the old one. Bump validation can be [turned off][validation].

| Old Version            | Command             | validate-bump | New Version          |
| ---------------------- | ------------------- | ------------- | -------------------- |
| `1.0.0-rc4+build.23`   | `release`           | True          | `1.0.0`              |
| `1.0.0`                | `release`           | True          | ValidationError      |
| `1.0.0`                | `release`           | False         | `1.0.0`              |

You can meaningfully use release chained with another commands, although the alternatives are perhaps more intuitive:

| Old Version            | Command              | New Version          |
| ---------------------- | -------------------- | -------------------- |
| `7.1.8-rc.1`           | `release,beta`       | `7.1.9-beta.1`       |
| `7.1.8-rc.1`           | `patch,beta`         | `7.1.9-beta.1`       |

## Build

The `build` command introduces the default build identifiers *build* and *1*. 
If some build identifiers are already present, and the last one *is a number*, it will be bumped.

Similar to the [pre-release][pre] command, you can specify you own custom build idetifier after `=`. 
Same as with pre-releases, this is prone to a [bug in python-semver][bug].

| Old Version            | Command             | New Version          |
| ---------------------- | ------------------- | -------------------- |
| `4.8.5-rc.2`           | `build`             | `4.8.5-rc.2+build.1` |
| `4.8.5-rc.2+build.1`   | `build`             | `4.8.5-rc.2+build.2` |
| `1.0.0`                | `build=fix-docs`    | `1.0.0+fix-docs.1`   |
| `1.0.0+fix-docs.1`     | `build`             | `1.0.0+fix-docs.2`   |
| `1.0.0+fix-docs.2`     | `build=docs-fixed`  | `1.0.0+fix-docs.3` <sup>[bug][bug]</sup> |

Build versions are all of the same precedence, so technically, a version bump does not occur.
Normally, [bump-validation][validation] checks whether the resulting version is higher than the old one. 
However, if all that changes is the build identifier, a version of equal precedence is sufficient to pass the validation. 

| Old Version            | Command             | validate-bump | New Version            |
| ---------------------- | ------------------- | ------------- | ---------------------- |
| `4.8.5-rc.2`           | `build=tracing`     | True          | `4.8.5-rc.2+tracing.1` |
| `4.8.5-rc.2+tracing.2` | `4.8.5-rc.2+debug`  | True          | `4.8.5-rc.2+debug`     |

### Development Build Shortcut

Sometimes people release what they call development builds, or *dev builds*.
A convenient shortcut for `build=dev` is `dev`.
Similar to the [alpha and beta][ab-short] shortcuts, `dev` is not an alias, so don't try to specify a custom build identifier with it.

| Old Version            | Command             | New Version          |
| ---------------------- | ------------------- | -------------------- |
| `2.9.3`                | `build=dev`         | `2.9.3+dev.1`        |
| `2.9.3`                | `dev`               | `2.9.3+dev.1`        |
| `2.9.3`                | `dev=develop`       | ValueError           |


### Alphanumeric Build Identifiers

Similar to [python-semver's][python-semver] inability to bump alphanumeric pre-release identifiers, alphanumeric build identifiers will also not be bumped <sup>[issue][issue]</sup>.
The returned result is the exact same version.
A ValidationError is not raised because when bumping or changing build identifiers, equal precedece of the old and new version is sufficient.

| Old Version            | Command             | validate-bump | New Version          |
| ---------------------- | ------------------- | ------------- | -------------------- |
| `6.3.4-rc.2+verbose`   | `build`             | True          | `6.3.4-rc.2+verbose` |

## Chained Commands

You can chain commands together by comma like this: `<command1>,<command2>,<command3>...`. 
They are executed one by one in the specified sequence. Some straight-forward and most common examples of chained commands are presented in the [pre-release][chained-pre] section.

The bump validation check is performed only after the last command is executed. 
It is therefore OK to temporarily violate the version precedence rule for the intermediate versions as long as the last resulting version passes the validation against the old version.

| Old Version            | Command             | validate-bump | New Version          |
| ---------------------- | ------------------- | ------------- | -------------------- |
| `8.0.4`                | `major,8.0.5`       | True          | `8.0.5`              |
| `8.0.4`                | `8.0.3,patch,build` | True          | `8.0.4+build.1`      |
| `8.0.4+build.1`        | `8.0.3,patch,build` | True          | `8.0.4+build.1`      |
| `8.0.4-alpha.1`        | `8.0.4,alpha,pre`   | True          | `8.0.4-alpha.2`      |


[validation]: https://hatch.pypa.io/latest/plugins/version-scheme/standard/#options
[bnf]: https://semver.org/#backusnaur-form-grammar-for-valid-semver-versions
[python-semver]: https://github.com/python-semver/python-semver
[bug]: https://github.com/python-semver/python-semver/issues/339
[issue]: https://github.com/python-semver/python-semver/issues/369
[specific-version]: #specific-version
[semver-regex]: https://regex101.com/r/Ly7O1x/3/
[chained-commands]: #chained-commands
[chained-pre]: #chained-with-a-version-core-bump
[pre]: #pre-release
[ab-short]: #alpha-beta-shortcuts
[build]: #build
