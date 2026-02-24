# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw.cmd.lint
import baw.utils
import tests


@tests.nightly
def test_linter_run_with_scope(example, capsys):
    root = str(example)
    returncode = baw.cmd.lint.lint(root)
    assert returncode == baw.SUCCESS, f'{returncode} {capsys.readouterr()}'

    # create error file
    todofile = os.path.join(root, 'xkcd/todo.py')
    baw.utils.file_create(todofile, '# TODO: Hello\n')

    returncode = baw.cmd.lint.lint(root)
    # assert returncode >= baw.FAILURE, f'{returncode} {capsys.readouterr()}'
    # error = tests.stdout(capsys)
    # assert 'W0511: TODO: Hello (fixme)' in error, error

    returncode = baw.cmd.lint.lint(root, scope=baw.cmd.lint.Scope.MINIMAL)
    assert returncode == baw.SUCCESS, f'{returncode} {capsys.readouterr()}'

    returncode = baw.cmd.lint.lint(root, scope=baw.cmd.lint.Scope.TODO)
    assert returncode >= baw.FAILURE, f'{returncode} {capsys.readouterr()}'

    returncode = baw.cmd.lint.lint(root, scope=baw.cmd.lint.Scope.ALL)
    # TODO: ENABLE LATER
    # assert returncode >= baw.FAILURE, f'{returncode} {capsys.readouterr()}'
    # replace todo error with "normal" error. todo must find nothing and
    # all or minimal detect it.
    baw.utils.file_replace(todofile, '# I am a newline error')
    returncode = baw.cmd.lint.lint(root, scope=baw.cmd.lint.Scope.TODO)
    assert returncode == baw.SUCCESS, f'{returncode} {capsys.readouterr()}'
    # no failure cause W0511 was removed/ code was replaced
    returncode = baw.cmd.lint.lint(root, scope=baw.cmd.lint.Scope.ALL)
    assert returncode == baw.SUCCESS, f'{returncode} {capsys.readouterr()}'


@tests.longrun
def test_linter_run_cli(example, monkeypatch):  # pylint:disable=W0613,W0621
    tests.baaw('lint todo', monkeypatch=monkeypatch)
