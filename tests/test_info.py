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
