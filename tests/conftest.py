#!/usr/bin/env python

import os
from typing import Generator

import pytest
from hatch.config.constants import AppEnvVars, ConfigEnvVars, PublishEnvVars
from hatch.utils.fs import Path, temp_directory

collect_ignore = [
    # "test_about.py",
    # "test_bump_instruction.py",
    # "test_changelog.py",
    # "test_hooks.py",
    # "test_semver_scheme.py",
]


@pytest.fixture(scope="session", autouse=True)
def isolation() -> Generator[Path, None, None]:
    with temp_directory() as d:
        data_dir = d / "data"
        data_dir.mkdir()
        cache_dir = d / "cache"
        cache_dir.mkdir()

        default_env_vars = {
            AppEnvVars.NO_COLOR: "1",
            ConfigEnvVars.DATA: str(data_dir),
            ConfigEnvVars.CACHE: str(cache_dir),
            PublishEnvVars.REPO: "dev",
            "HATCH_SELF_TESTING": "true",
            "GIT_AUTHOR_NAME": "Foo Bar",
            "GIT_AUTHOR_EMAIL": "foo@bar.baz",
            "COLUMNS": "80",
            "LINES": "24",
        }
        with d.as_cwd(default_env_vars):
            os.environ.pop(AppEnvVars.ENV_ACTIVE, None)
            yield d
