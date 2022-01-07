# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
import os

import baw.cmd.ide
import baw.config
import baw.utils


def test_ide_open(testdir, monkeypatch):
    workspace = str(testdir)

    name = 'short'

    baw.config.create(workspace, name, 'description')
    testdir.mkpydir(name)
    baw.utils.file_append(
        os.path.join(workspace, name, '__init__.py'),
        '__version__ = "1.0.0"\n',
    )
    # test folder
    testdir.mkpydir('tests')

    with monkeypatch.context() as patched:
        # do not open ide
        patched.setattr(baw.cmd.ide, 'start', lambda root: baw.utils.SUCCESS)
        baw.cmd.ide.ide_open(workspace)
