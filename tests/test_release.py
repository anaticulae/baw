# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw
import tests


def test_release_already_done(simple, capsys):
    simple[0](
        '--verbose release',
        expect=False,
        verbose=2,
    )
    stdout = tests.stdout(capsys)
    assert 'head is already: v0.0.0' in stdout


MESSAGE = 'The next version is: 1.0.0'


@tests.longrun
def test_release_simple(simple, monkeypatch, capsys):
    root = simple[1]
    path = os.path.join(root, 'abc.txt')
    baw.file_create(path, 'CONTENT')
    baw.git_add(root, 'abc.txt')
    baw.git_commit(root, '.', 'feat(abc): feature is welcome')
    with monkeypatch.context():
        # do not open ide
        simple[0]('-v release --no_push')
    output = capsys.readouterr()
    # semantic release writes log to std-err
    assert MESSAGE in output.err


def test_release_do_not_drop_first_release(simple, capsys):
    simple[0](
        'release drop',
        expect=False,
    )
    stderr = tests.stderr(capsys)
    assert 'Could not remove v0.0.0 release' in stderr


@tests.hasbaw
@tests.hasgit
@tests.longrun
def test_release_non_python(testdir, monkeypatch, capsys):
    cmd = 'init wasd "bla bla bal" --type=data'
    tests.baaw(cmd, monkeypatch)
    no_remote()
    root = testdir.tmpdir
    path = os.path.join(root, 'abc.txt')
    baw.file_create(path, 'CONTENT')
    baw.git_add(root, 'abc.txt')
    baw.git_commit(root, '.', 'feat(abc): feature is welcome')
    with monkeypatch.context():
        # do not open ide
        cmd = '-v release --no_push'
        tests.baaw(cmd, monkeypatch)
    output = capsys.readouterr()
    # semantic release writes log to std-err
    assert MESSAGE in output.err


def no_remote():
    tests.run('git remote remove origin')
    tests.run('git remote add origin https://rando23203142smddmd.com/fake/repo.git') # yapf:disable
