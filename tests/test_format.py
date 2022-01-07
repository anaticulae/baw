# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
import os
import subprocess

import pytest

import baw.config
import baw.runtime
import baw.utils


@pytest.fixture
def simpleproject(testdir):
    root = str(testdir)
    baw.config.create(root, 'abc', 'alphabet')
    baw.utils.file_create('setup.py', '# setup')

    abc = os.path.join(root, 'abc')
    os.makedirs(abc)
    return root


def test_regression_format_keep_single_list(simpleproject):  # pylint:disable=W0621
    """Do not use -k, as a result renaming does not work propper.

    import hello.abc as ha produces:

    import hello.abc
    import hello.abc as ha

    We do not want this first line.
    """
    source = 'import baw.utils as bu\n'

    path = os.path.join(simpleproject, 'abc/hello.py')
    baw.utils.file_create(path, source)
    assert os.path.exists(path)

    completed = subprocess.run('baw --format', check=False)
    assert completed.returncode == baw.utils.SUCCESS

    read = baw.utils.file_read(path)
    assert read == source
