# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import pytest
import utilatest

import baw.config.change
import baw.utils
import tests


def test_cmd_test_cov_simple(simple, capsys):
    # capsys does not capture simple run, therefore I build this workaround.
    simple[0]('test --cov -n1')
    simple[0]('info covreport')
    lines = tests.stdout(capsys).strip().splitlines()
    path = os.path.join(lines[-1], 'index.html')
    content = baw.utils.file_read(path)
    assert '100%' in content


@pytest.mark.parametrize('report', (True, False))
def test_cmd_test_cov_report(report, simple, capsys):
    noreport = '' if report else '--no_report'
    # do not generate html-report
    simple[0](f'--verbose test --cov -n1 {noreport}')
    stdout = tests.stdout(capsys)
    if report:
        assert '--cov-report=html:' in stdout
    else:
        assert '--cov-report=html:' not in stdout


MISSING_TEST_RESOURCE = """
[project]
short = invalid_test
name = IT
source = it
    missing
"""


def test_cmd_test_cov_no_root(testdir, monkeypatch, capsys):
    baw.utils.file_create(
        '.baw',
        MISSING_TEST_RESOURCE,
    )
    os.mkdir(testdir.tmpdir.join('tests'))
    tests.baaw(
        'test --cov -n1',
        monkeypatch,
        expect=False,
    )
    stdout = tests.stdout(capsys)
    assert 'subproject does not exists: it' in stdout
    assert 'subproject does not exists: missing' in stdout


def test_cmd_cov_increase(simple):
    root = simple[1]
    assert baw.config.coverage_min(root) == baw.config.COVERAGE_MIN
    baw.config.change.coverage_min(root, 50.0)
    assert baw.config.coverage_min(root) == 50.0
    baw.config.change.coverage_min(root, 60.0)
    assert baw.config.coverage_min(root) == 60.0


@utilatest.no_linux
def test_cmd_cov_upgrade_max_done(simple, capsys):
    simple[0]('cov upgrade')
    stdout = tests.stdout(capsys)
    assert 'max cov reached:' in stdout


@utilatest.no_linux
def test_cmd_cov_print(simple, capsys):
    simple[0]('cov print')
    stdout = tests.stdout(capsys)
    assert '100' in stdout
