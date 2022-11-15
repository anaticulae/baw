# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import os
import sys
import textwrap

import baw.config
import baw.git
import baw.resources
import baw.utils

AUTO = 'commit_author = Automated Release <automated_release@ostia.la>'
ME = 'commit_author = Helmut Konrad Fahrendholz <helmutus@outlook.com>'


@contextlib.contextmanager
def temp_semantic_config(root: str, verbose: bool, venv: bool = False):
    version = baw.config.version(root)
    replaced = baw.resources.SETUP_CFG.replace('{{VERSION}}', version)
    changelog_path = baw.config.changelog(root)
    replaced = replaced.replace('{{CHANGELOG}}', changelog_path)
    if replaced == baw.resources.SETUP_CFG:
        baw.utils.error('while replacing template')
        sys.exit(baw.utils.FAILURE)
    if 'VERSION' in version:
        replaced = replaced.replace(AUTO, ME)
        # do not use gitea token
        replaced = replaced.replace('gitea_token_var=GITEA_TOKEN', '')
    # use own tmpfile cause TemporaryFile(delete=True) seems no supported
    # at linux, parameter delete is missing.
    config = os.path.join(root, 'setup.cfg')
    baw.utils.file_replace(config, replaced)
    if not firstversion(root):
        changelog = determine_changelog(root, verbose, venv=venv)
        baw.utils.file_append(config, f'commit_message={changelog}')
    else:
        baw.utils.file_append(config, 'commit_message=Initial Release')
    yield config
    # remove file
    os.unlink(config)


def determine_changelog(root: str, verbose: bool, venv: bool = False) -> str:
    cmd = 'baw_semantic_release changelog '
    cmd += version_variables(root)
    cmd += '-D "changelog_components=baw.changelog.changelog_headers" '
    cmd += '--unreleased'
    completed = baw.runtime.run_target(
        root,
        cmd,
        verbose=verbose,
        venv=venv,
    )
    changelog = completed.stdout
    result = textwrap.indent(changelog, prefix='    ')
    result = result.strip()
    result = result.replace('###', '>>>')
    result = result.replace('##', '>>')
    return result


def version_variables(root: str) -> str:
    short = baw.config.version(root)
    result = f'-D "version_variable={short}" '
    return result


def firstversion(root: str) -> bool:
    if not baw.git.headhash(root):
        return True
    return False
