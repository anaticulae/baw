# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw.git
import baw.resources
import baw.utils


def init(
    root: str,
    verbose: bool = False,
    venv: bool = False,
):
    source = jenkinsfile(root)
    replaced = baw.resources.template_replace(
        root,
        template=baw.resources.JENKINSFILE,
    )
    with baw.git.git_stash(root, verbose=verbose, virtual=venv):
        baw.utils.file_create(
            source,
            content=replaced,
        )
        failure = baw.git.git_commit(
            root,
            source=source,
            message='chore(ci): add Jenkinsfile',
            verbose=verbose,
        )
        if failure:
            return failure
    return baw.utils.SUCCESS


def jenkinsfile(root: str):
    return os.path.join(root, 'Jenkinsfile')


def extend_cli(parser):
    sync = parser.add_parser('pipeline', help='Run pipline task')
    sync.add_argument(
        'create',
        help='manage the jenkins file',
        nargs='?',
        const='test',
        choices='init upgrade test'.split(),
    )
