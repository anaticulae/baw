# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import functools
import os

import pytest

import baw.utils
import tests

BASE = """\
[project]
short = jenkins
name = lets test the jenkinsfile
"""


@pytest.fixture
def simple(testdir, monkeypatch):
    baw.utils.file_create(
        testdir.tmpdir.join('.baw'),
        content=BASE,
    )
    runner = functools.partial(tests.run_command, monkeypatch=monkeypatch)
    yield runner, testdir.tmpdir


@pytest.mark.xfail(reason='incomplete impl')
def test_cmd_pipeline_init(simple):  # pylint:disable=W0621
    simple[0]('pipeline init')
    assert os.path.exists(simple[1].join('Jenkinsfile'))
