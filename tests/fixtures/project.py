# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import functools
import os
import textwrap

import pytest

import baw.config
import baw.git
import baw.runtime
import baw.utils
import tests

EXAMPLE_PROJECT_NAME = 'xkcd'


@pytest.fixture
def example(testdir, monkeypatch):
    """Creating example project due console"""
    if tests.run('which baw').returncode:
        pytest.skip('install baw')
    if not baw.git.installed():
        pytest.skip('install git')
    baw.git.update_userdata()
    cmd = f'baw --verbose init {EXAMPLE_PROJECT_NAME} "Longtime project"'
    with monkeypatch.context() as context:
        tmpdir = lambda: testdir.tmpdir.join('tmpdir')  # pylint:disable=C3001
        context.setattr(baw.config, 'bawtmp', tmpdir)
        with tests.assert_run(cmd, cwd=testdir.tmpdir):
            assert os.path.exists(os.path.join(testdir.tmpdir, '.git'))
            yield testdir.tmpdir


@pytest.fixture
def simple(example, monkeypatch):  # pylint:disable=W0621
    runner = functools.partial(
        tests.baaw,
        monkeypatch=monkeypatch,
    )
    yield runner, example


@pytest.fixture
def project_example(testdir, monkeypatch):
    if baw.runtime.run('which baw', cwd=testdir.tmpdir).returncode:
        pytest.skip('install baw')
    if not baw.git.installed():
        pytest.skip('install git')
    with monkeypatch.context() as context:
        tmpdir = lambda: testdir.tmpdir.join('tmpdir')  # pylint:disable=C3001
        context.setattr(baw.config, 'bawtmp', tmpdir)
        baw.git.update_userdata()
        tests.baaw(['init', 'xcd', '"I Like This Project"'], monkeypatch)
        tests.baaw('plan new', monkeypatch)
        yield testdir.tmpdir


@pytest.fixture
def project_example_done(project_example):  # pylint:disable=W0621
    # fake to add a done todo
    pattern = textwrap.dedent("""\
    RP 0.1.0
    =========
    """)
    replacement = textwrap.dedent("""\
    RP 0.1.0
    =========

    * [x] this is a faked done todo
    """)
    source = os.path.join(project_example, 'docs/releases/0.1.0.rst')
    loaded = baw.utils.file_read(source)
    replaced = loaded.replace(pattern, replacement)
    baw.utils.file_replace(source, replaced)
    return project_example


RUN = """
[run]
command = ls
"""


@pytest.fixture
def project_with_command(example):  # pylint:disable=W0621
    """Create testproject which contains --run-command ls."""
    path = baw.config.config_path(example)
    baw.utils.file_append(path, RUN)
    return example


@pytest.fixture
def project_with_test(example):  # pylint:disable=W0621
    """Create project with one test case"""
    test_me = textwrap.dedent("""\
        def test_me():
            # Empty passing test
            pass
    """)
    write = example.join('tests/my_test.py')
    baw.utils.file_create(write, test_me)
    assert os.path.exists(write)
    return example
