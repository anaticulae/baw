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
import baw.runtime
import tests

CREATE_FILE = """
import baw
def test_write():
    baw.file_append('tests/abc', 'abc')
"""


def test_cmd_baseline_test(simple, monkeypatch, capsys):
    root = simple[1]
    baw.file_create(os.path.join(root, 'tests/abc'), 'abc')
    baw.file_create(
        os.path.join(root, 'tests/test_write.py'),
        content=CREATE_FILE,
    )
    baw.git_add(root, pattern='*')
    baw.git_commit(root, source='.', message='baseline')
    assert baw.git_isclean(root)
    with monkeypatch.context() as context:
        push = lambda _: baw.SUCCESS
        # disable pushing to gitea
        context.setattr(baw.gix, 'push', push)
        simple[0]('baseline test -n1')
    stdout = tests.stdout(capsys)
    assert 'enable overwriting: BASELINE_REPLACE' in stdout, stdout
    # TODO: EXTEND VERIFICATION
