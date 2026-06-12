#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import utilo

import baw
import baw.cmd.sync
import tests

# @tests.longrun
# @pytest.mark.parametrize('venv', [False, True])
# def test_sync(venv):
#     if venv and not baw.runtime.has_virtual(baw.ROOT):
#         pytest.skip('generate venv')
#     baw.cmd.sync.sync(baw.ROOT, venv=venv, verbose=False)


@tests.longrun
def test_sync_novenv():
    baw.cmd.sync.sync(
        baw.ROOT,
        verbose=False,
    )


def test_pip_list():
    parsed = baw.cmd.sync.pip_list(baw.ROOT)
    assert len(parsed.equal) >= 10, parsed.equal


PYPROJECT = """\
[project]
name = "writers"
version = "0.11.3"
description = ""
requires-python = ">=3.12"
authors = [
{ name = "Helmut Konrad Schewe", email = "helmutus@outlook.com" },
]
dependencies = [
]

[project.optional-dependencies]
dev = [
# already definded in baw-project, overwrite it!
"pytest-localserver>=0.10.0,<1.0.0",
]

"""


@tests.longrun
def test_sync_duplicated_package_definition(project_example):
    """Prefere local requirements over baw-requirements. Avoid duplicated
    requirements which are in baw and project definition."""
    path = utilo.join(project_example, baw.PYPROJECT)
    utilo.file_replace(path, PYPROJECT)
    tests.assert_run('baw sync all', cwd=project_example).__enter__()
