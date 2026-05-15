# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import pytest
import utilo

import baw.cmd.format
import baw.config
import tests


@pytest.fixture
def minimal(testdir):
    baw.config.create(testdir.tmpdir, 'abc', 'alphabet')
    utilo.file_create('pyproject.toml', '# setup')
    os.makedirs(testdir.tmpdir.join('abc'))
    return testdir.tmpdir


@tests.hasbaw
def test_regression_format_keep_single_list(minimal, monkeypatch):  # pylint:disable=W0621
    """Do not use -k, as a result renaming does not work propper.

    import hello.abc as ha produces:

    import hello.abc
    import hello.abc as ha

    We do not want this first line.
    """
    source = 'import baw.utils as bu\n'
    path = os.path.join(minimal, 'abc/hello.py')
    utilo.file_create(path, source)
    assert os.path.exists(path)
    tests.baaw('format', monkeypatch=monkeypatch)
    read = utilo.file_read(path)
    assert read == source


VALID = """\
---
version: 2

updates:
  # Python dependencies
  - package-ecosystem: pip
    directory: /  # only checks requirements.txt
    schedule:
      interval: weekly
"""


def test_format_yaml(testdir):
    utilo.file_create('valid.yml', content=VALID)
    returncode = baw.cmd.format.format_yaml(testdir.tmpdir)
    assert not returncode


INVALID_YAML = """\
[build-system]
requires = [
    "setuptools>=82.0.1",
    "wheel>=0.46.3",
]
build-backend = "setuptools.build_meta"
{{SHORT}}
"""


def test_format_toml_invalid(testdir):
    # format toml as yaml to invoke error
    utilo.file_create('invalid.toml', content=INVALID_YAML)
    with pytest.raises(SystemExit):
        returncode = baw.cmd.format.format_toml(testdir.tmpdir, filters=False)
        assert returncode
