# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import pytest

import tests


@pytest.mark.parametrize('cmd, expected', (
    ('covreport', 'report'),
    ('tmp', 'tmp'),
    ('venv', 'venv'),
))
def test_cmd_info(cmd, expected, monkeypatch, capsys):
    tests.baaw(
        f'info {cmd}',
        monkeypatch,
    )
    stdout = tests.stdout(capsys)
    assert expected in stdout, str(stdout)


def test_cmd_requirement_info(monkeypatch, capsys):
    tests.baaw(
        'info requirement',
        monkeypatch,
    )
    stdout = tests.stdout(capsys)
    # ensure that stdout only procudes a single int
    hashed = int(stdout)  # pylint:disable=W0612


def test_cmd_info_venv_fix(monkeypatch, capsys):
    """\
    Exepect `c/tmp/dev/tmp/baw`
    not `venv: /c/tmp/dev/
         c/tmp/dev/tmp/baw`
    """
    cmd = '--venv info tmp'
    tests.baaw(cmd, monkeypatch, verbose=False)
    stdout = tests.stdout(capsys)
    assert 'venv:' not in stdout
    assert ' ' not in stdout.strip()
