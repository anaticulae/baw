# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utilo

import baw.cmd.release.config
import baw.runtime


def run(root, verbose, release_type, no_push: bool = False):
    baw.log('update version tag')
    with baw.cmd.release.config.release_config_tmp(
            root,
            verbose,
    ):
        returncode = run_release(
            root,
            no_push=no_push,
            release_type=release_type,
            verbose=verbose,
        )
    if returncode:
        baw.error('while running semantic-release')
        return returncode
    return baw.SUCCESS


def run_release(
    root: str,
    no_push: bool = True,
    release_type: str | None = None,
    verbose: int = 0,
) -> int:
    cmd = 'semantic-release '
    if is_dataproject(root):
        cmd += '-c VERSION '
    else:
        cmd += '-c pyproject.toml '
    if verbose:
        level = 'v' * verbose
        cmd += f'-{level} '
    cmd += '--strict '
    cmd += 'version '
    if no_push:
        cmd += ' --no-push'
    if release_type:
        if release_type in 'majorminorpatch':
            # major minor patch
            cmd += f' --{release_type}'
    completed = baw.runtime.run_target(
        root,
        cmd,
        verbose=verbose,
    )
    if NO_RELEASE_MESSAGE in completed.stderr.lower():
        return baw.FAILURE
    if completed.stderr:
        baw.error(completed.stderr)
    baw.log(completed.stdout)

    return completed.returncode


def is_dataproject(root) -> bool:
    if utilo.exists(utilo.join(root, 'VERSION')):
        return True
    return False


# semantic release returns this message if no new release is provided, cause
# of the absent of new features/bugfixes.
NO_RELEASE_MESSAGE = 'no release will be made'


def select_release_type(typ: str, cfg: str) -> str:
    # Only release with type if user select one. If the user does
    # select a release-type let semantic release decide. If only some
    # style are commited but we want the release, we have to overwrite
    # default action.
    if require_autopatch(utilo.file_read(cfg)):
        typ = 'patch'
    typ = '' if typ == 'auto' else f'--{typ}'
    return typ


def require_autopatch(changelog_content: str) -> bool:
    for item in 'Feature Fix Documentation'.split():  # pylint:disable=C0501
        if f'>>> {item}' in changelog_content:
            return False
    return True
