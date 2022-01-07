# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import sys

import pytest

import baw.run


@pytest.mark.parametrize(
    'command',
    [
        '',
        '-h',
        '-v',
        # ['--format'], problem with multiprocessing tests/xdist
    ])
def test_run_command(monkeypatch, command):
    """Run help and version and format command to reach basic test coverage"""
    with monkeypatch.context() as context:
        # Remove all environment vars
        # baw is removed as first arg
        context.setattr(sys, 'argv', ['baw'] + command.split())
        with pytest.raises(SystemExit) as result:
            baw.run.main()
        result = str(result)
        assert 'SystemExit(0)' in result, result


def assert_success(result):
    result = str(result)
    assert 'SystemExit(0)' in result, result
