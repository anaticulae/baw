# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import sys

import pytest

import baw.__main__


@pytest.mark.parametrize(
    'cmd',
    [
        '',
        '-h',
        '-v',
        # ['--format'], problem with multiprocessing tests/xdist
    ])
def test_baaw(monkeypatch, cmd):
    """Run help and version and format cmd to reach basic test coverage"""
    with monkeypatch.context() as context:
        # Remove all environment vars
        # baw is removed as first arg
        context.setattr(sys, 'argv', ['baw'] + cmd.split())
        with pytest.raises(SystemExit) as result:
            baw.__main__.run()
        result = str(result)
        # if no cmd is selected print help message and return code 1
        expected = 'SystemExit(0)' if cmd else 'SystemExit(1)'
        assert expected in result, result


def assert_success(result):
    result = str(result)
    assert 'SystemExit(0)' in result, result
