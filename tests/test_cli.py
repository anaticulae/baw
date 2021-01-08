# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Test runnig commands with --command."""

import pytest

import baw.config
import baw.utils
import tests
from tests import example

RUN = """
[run]
command = ls
"""


@pytest.fixture
def project_with_command(example):  #pylint: disable=W0621
    """Create testproject which contains --run-command ls."""
    path = baw.config.config_path(example)
    baw.utils.file_append(path, RUN)
    return example


@tests.skip_longrun
def test_run_commands_with_ls(project_with_command):  #pylint: disable=W0621
    """Running --run with ls."""
    tmpdir = project_with_command
    tests.assert_run('baw --run', cwd=tmpdir)


project_without_command = example  #pylint: disable=C0103


@tests.skip_longrun
def test_run_without_commands_in_project(project_without_command):  #pylint: disable=W0621
    """Running --run without any registered command in project."""
    tmpdir = project_without_command
    tests.assert_run_fail('baw --run', cwd=tmpdir)
