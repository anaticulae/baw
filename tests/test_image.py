# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw.cmd.image.dockerfiles
import tests


def test_cmd_image_create(simple, capsys):  # pylint:disable=W0621,W0613
    simple[0]('pipe init')
    simple[0]('image create')


def test_image_create(simple, capsys):  # pylint:disable=W0621,W0613
    # docker file requires existing Jenkinsfile
    simple[0]('pipe init')
    with baw.cmd.image.dockerfiles.generate(simple[1]) as path:
        assert os.path.exists(path)


def test_cmd_image_newest(monkeypatch, capsys):
    name = '169.254.149.20:6001/arch_python_git_baw:v1.26.0'
    cmd = f'image newest --name {name}'
    tests.baaw(cmd, monkeypatch=monkeypatch)
    stdout = tests.stdout(capsys)
    assert '169.254.149.20:6001/arch_python_git_baw:v' in stdout


def test_cmd_image_upgrade_prerelease(simple, capsys):
    simple[0]('pipe init')
    simple[0]('image upgrade --prerelease --dockerfile Jenkinsfile')
    stdout = tests.stdout(capsys)
    assert 'start upgrading:' in stdout
    upgraded = 'upgraded:' in stdout
    upgraded |= 'up-to-date:' in stdout
    assert upgraded, str(stdout)
