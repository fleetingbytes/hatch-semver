# hatch-semver

A plugin for [hatch][hatch] to support [semantic versioning][semver].


## Usage

Introduce *hatch-semver* as a build-dependency to your project (in `pyproject.toml`):

```toml
[build-system]
requires = [
    "hatchling>=1.8.0",
    "hatch-semver",
]
build-backend = "hatchling.build"
```

Further down in `pyproject.toml`, where you specify your project's version, set version scheme
to `semver`:
```toml
[tool.hatch.version]
path = "src/<your_project>/__about__.py"
scheme = "semver"
```

You can then use hatch's usual [versioning commands][hatch_versioning] to bump your project's
version in a semver-compliant way.

[hatch]: hatch.pypa.io/
[semver]: https://semver.org/
[hatch_versioning]: https://hatch.pypa.io/latest/version/#updating
