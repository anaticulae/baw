# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw.cmd.release.pack
import baw.git
import baw.utils
import tests


def test_release_already_done(simple, capsys):
    simple[0]('--verbose release')
    stdout = tests.stdout(capsys)
    assert 'head is already: v0.0.0' in stdout


@tests.longrun
def test_release_simple(simple, monkeypatch, capsys):
    root = simple[1]
    path = os.path.join(root, 'abc.txt')
    baw.utils.file_create(path, 'CONTENT')
    baw.git.add(root, 'abc.txt')
    baw.git.commit(root, '.', 'feat(abc): feature is welcome')
    with monkeypatch.context() as patched:
        # do not open ide
        patched.setattr(baw.cmd.release.pack, 'release_cmd', lambda _, __: 'ls')
        simple[0]('--verbose release')
    stdout = tests.stdout(capsys)
    assert 'Completed: `ls` in' in stdout
