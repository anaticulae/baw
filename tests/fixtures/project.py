# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import textwrap

import pytest

import baw.config
import baw.git
import baw.utils
import tests


@pytest.fixture
def project_example(testdir, monkeypatch):
    with monkeypatch.context() as context:
        tmpdir = lambda: testdir.tmpdir.join('tmpdir')
        context.setattr(baw.config, 'bawtmp', tmpdir)

        baw.git.update_userdata()
        tests.run_command(['init', 'xcd', '"I Like This Project"'], monkeypatch)
        tests.run_command('plan new', monkeypatch)
        tests.run_command(['--virtual'], monkeypatch)

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
def project_with_command(example):
    """Create testproject which contains --run-command ls."""
    path = baw.config.config_path(example)
    baw.utils.file_append(path, RUN)
    return example
