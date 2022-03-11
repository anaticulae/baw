# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Test runnig commands with --command."""

import tests


@tests.longrun
def test_run_commands_with_ls(project_with_command):
    """Running --run with ls."""
    tmpdir = project_with_command
    tests.assert_run('baw --run', cwd=tmpdir)


@tests.longrun
def test_run_without_commands_in_project(example):
    """Running --run without any registered command in project."""
    tests.assert_run_fail(
        'baw --run',
        cwd=example,
    )
