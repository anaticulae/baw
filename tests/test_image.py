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

import baw
import baw.cmd.image.dockerfiles
import baw.pipefile
import baw.utils
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
    name = baw.pipefile.docker_image(baw.ROOT)
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


@pytest.mark.parametrize('typ', [
    'PIPREF',
    'PIPSTABLE',
])
def test_cmd_image_pipref_upgrade(simple, capsys, typ):
    simple[0]('pipe init')
    root = simple[1]
    dockerfile = os.path.join(root, 'DOCKERFILE')

    def create():
        # use image-name of current Jenkins-File
        content = baw.cmd.image.dockerfiles.header(baw.ROOT)
        # create simple docker-file which replaces <<PIPREF>><<PIPSTABLE>>
        content += f'\nRUN echo <<{typ}>>'
        return content

    baw.utils.file_create(dockerfile, create())
    baw.git_commit(root, 'DOCKERFILE', 'verify pipref')
    tmpname = f'tmp_baw_test_cmd_image_pipref_{typ.lower()}'
    # create dockerfile to verify PIPREF-replacement
    simple[0](f'image create --dockerfile {dockerfile} --name={tmpname}')
    expected = 'RUN echo xkcd==0.0.0'
    # ensure that replacement was correct
    stdout = tests.stdout(capsys)
    assert expected in stdout
