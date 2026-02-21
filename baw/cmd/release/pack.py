# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw.cmd.release.config
import baw.runtime
import baw.utils


def run(root, verbose, release_type, venv: bool = False):
    baw.log('update version tag')
    with baw.cmd.release.config.temp_semantic_config(
            root,
            verbose,
            venv=venv,
    ):
        returncode = changelog(root)
        returncode += version(root)
    if returncode:
        baw.error('while running semantic-release')
        return returncode
    return baw.SUCCESS


def changelog(root: str):
    cfg = os.path.join(root, "release.cfg")
    cmd = f'semantic-release -c {cfg} changelog'
    completed = baw.runtime.run_target(
        root,
        cmd,
    )
    baw.log(completed)
    return completed.returncode


def version(root: str):
    cfg = os.path.join(root, "release.cfg")
    cmd = f'semantic-release -c {cfg} version --no-push'
    completed = baw.runtime.run_target(
        root,
        cmd,
    )
    baw.log(completed)
    return completed.returncode


# semantic release returns this message if no new release is provided, cause
# of the absent of new features/bugfixes.
NO_RELEASE_MESSAGE = 'No release will be made.'


def select_release_type(typ: str, cfg: str) -> str:
    # Only release with type if user select one. If the user does
    # select a release-type let semantic release decide. If only some
    # style are commited but we want the release, we have to overwrite
    # default action.
    if require_autopatch(baw.utils.file_read(cfg)):
        typ = 'patch'
    typ = '' if typ == 'auto' else f'--{typ}'
    return typ


def require_autopatch(changelog: str) -> bool:
    for item in 'Feature Fix Documentation'.split():  # pylint:disable=C0501
        if f'>>> {item}' in changelog:
            return False
    return True
