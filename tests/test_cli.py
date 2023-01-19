# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Test runnig cmds with --cmd."""

import os

import baw.utils
import tests


@tests.longrun
def test_baaws_with_ls(project_with_cmd):
    """Running --run with ls."""
    tmpdir = project_with_cmd
    tests.assert_run('baw --run', cwd=tmpdir)


@tests.longrun
def test_run_without_cmds_in_project(example):
    """Running --run without any registered cmd in project."""
    tests.assert_run_fail(
        'baw --run',
        cwd=example,
    )


def test_cmd_test_cov_simple(simple, capsys):
    # capsys does not capture simple run, therefore I build this workaround.
    simple[0]('test --cov -n1')
    simple[0]('info covreport')
    lines = tests.stdout(capsys).strip().splitlines()
    path = os.path.join(lines[-1], 'index.html')
    content = baw.utils.file_read(path)
    assert '100%' in content
