# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import baw.cmd.release.config
import baw.runtime
import baw.utils


def run(root, verbose, release_type, venv: bool = False):
    baw.utils.log('update version tag')
    with baw.cmd.release.config.temp_semantic_config(
            root,
            verbose,
            venv=venv,
    ) as cfg:
        cmd = release_cmd(release_type, cfg)
        completed = baw.runtime.run_target(
            root,
            cmd,
            verbose=verbose,
            venv=venv,
        )
        baw.utils.log(completed.stdout)
        if NO_RELEASE_MESSAGE in completed.stdout:
            baw.utils.error('abort release')
            baw.utils.log('ensure that some (feat) are commited')
            baw.utils.log('use: `baw release minor` to force release')
            return baw.utils.FAILURE
    if completed.returncode:
        baw.utils.error('while running semantic-release')
        baw.utils.error(completed.stderr)
        return completed.returncode
    return baw.utils.SUCCESS


def release_cmd(types, cfg) -> str:
    release_type = select_release_type(types, cfg=cfg)
    result = f'baw_semantic_release -v DEBUG publish {release_type}'
    return result


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
