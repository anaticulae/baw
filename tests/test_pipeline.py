# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import pytest


def test_cmd_pipeline_init(simple):
    simple[0]('pipe init')
    assert os.path.exists(simple[1].join('Jenkinsfile'))


def test_cmd_pipeline_lib_error(simple, capsys):
    with pytest.raises(AssertionError, match='ExceptionInfo SystemExit'):
        simple[0]('pipe library')
    assert not os.path.exists(simple[1].join('Jenkinsfile'))
    assert 'could not find Jenkinsfile' in stderr(capsys)


def test_cmd_pipeline_lib_upgrade(simple):
    simple[0]('pipe init')
    # upgrade
    simple[0]('pipe library')


def test_cmd_pipeline_lib_already_upgraded(simple, capsys):
    simple[0]('pipe init')
    simple[0]('pipe library')  # upgrade
    with pytest.raises(AssertionError, match='ExceptionInfo SystemExit'):
        simple[0]('pipe library')  # already upgraded
    assert 'already newst caelum' in stderr(capsys)


def stderr(capsys):
    return capsys.readouterr().err
