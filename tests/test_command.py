# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Test runnig commands with --command."""

from os.path import join

from pytest import fixture

from baw.config import PROJECT_PATH
from baw.utils import file_append
from tests import assert_run
from tests import assert_run_fail
from tests import example

RUN = """
[run]
command = ls
"""


@fixture
def project_with_command(example):  #pylint: disable=W0621
    """Create testproject which contains --run-command ls."""
    config = join(example, PROJECT_PATH)
    file_append(config, RUN)
    return example


def test_run_commands_with_ls(project_with_command):  #pylint: disable=W0621
    """Running --run with ls."""
    tmpdir = project_with_command
    assert_run('baw --run', cwd=tmpdir)


project_without_command = example  #pylint: disable=C0103


def test_run_without_commands_in_project(project_without_command):  #pylint: disable=W0621
    """Running --run without any registered command in project."""
    tmpdir = project_without_command
    assert_run_fail('baw --run', cwd=tmpdir)
