# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Test runnig cmds with --cmd."""

import tests


@tests.longrun
def test_cli_baaws_with_ls(project_with_cmd):
    """Running --run with ls."""
    tests.assert_run('baw sh ls', cwd=project_with_cmd).__enter__()


@tests.longrun
def test_cli_run_without_cmds_in_project(example):
    """Running --run without any registered cmd in project."""
    tests.assert_run_fail('baw sh', cwd=example).__enter__()
