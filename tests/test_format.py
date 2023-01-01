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

import baw.config
import baw.utils
import tests


@pytest.fixture
def minimal(testdir):
    baw.config.create(testdir.tmpdir, 'abc', 'alphabet')
    baw.utils.file_create('setup.py', '# setup')
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
    baw.utils.file_create(path, source)
    assert os.path.exists(path)
    tests.baaw('format', monkeypatch=monkeypatch)
    read = baw.utils.file_read(path)
    assert read == source
