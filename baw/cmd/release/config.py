# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import functools
import os
import textwrap

import baw.config
import baw.gix
import baw.project
import baw.resources
import baw.utils

AUTOMATED = 'Automated Release <automated_release@ostia.la>'


@contextlib.contextmanager
def temp_semantic_config(root: str, verbose: bool, venv: bool = False):
    generated = str(ReleaseConfig(root, verbose, venv))
    # use own tmpfile cause TemporaryFile(delete=True) seems no supported
    # at linux, parameter delete is missing.
    config = os.path.join(root, 'setup.cfg')
    baw.utils.file_replace(config, generated)
    yield config
    # remove file
    os.unlink(config)


class ReleaseConfig:

    def __init__(self, root: str, verbose: bool = False, venv: bool = False):
        r"""\
        >>> str(ReleaseConfig(__file__))
        '[semantic_release]\n...commit_author=Autom...<...@ostia.la>\nversion_variable=...:__version__\nchangelog_file=CHANGELOG\n...=GITEA_TOKEN\ncommit_message=...'
        """
        self.root = baw.project.determine_root(root)
        self.verbose = verbose
        self.venv = venv

    @property
    def commit_author(self) -> str:
        author = AUTOMATED
        if not baw.config.basic(self.root):
            author_name = baw.config.git_author_name()
            author_email = baw.config.git_author_email()
            author = f'{author_name} <{author_email}>'
        return f'commit_author={author}'

    @property
    def version_variable(self) -> str:
        value = baw.config.version(self.root)
        return f'version_variable={value}'

    @property
    def changelog_file(self) -> str:
        value = baw.config.changelog(self.root)
        return f'changelog_file={value}'

    @property
    def changelog_header(self) -> str:
        r"""\
        >>> ReleaseConfig(__file__).changelog_header
        'changelog_placeholder=# Changelog\n\n    Every noteable change is logged here.\n\n'
        """
        path = baw.config.changelog(self.root)
        content = baw.utils.file_read(path)
        header = content.split('## v')[0]
        splitted = header.splitlines(True)
        collected = [splitted[0]] if splitted else []
        if splitted:
            for line in splitted[1:]:
                if not line.strip():
                    collected.append(line)
                    continue
                collected.append('    ' + line)
        result = f'changelog_placeholder={"".join(collected)}'
        return result

    @property
    def gitea_token_var(self) -> str:
        if not baw.config.basic(self.root):
            return ''
        return 'gitea_token_var=GITEA_TOKEN'

    @functools.cached_property
    def commit_message(self) -> str:
        """\
        >>> ReleaseConfig(__file__).commit_message
        'commit_message=...'
        """
        if firstversion(self.root):
            return 'commit_message=Initial Release'
        changelog = determine_changelog(
            self.root,
            self.verbose,
            venv=self.venv,
        )
        return f'commit_message={changelog}'

    def __str__(self) -> str:
        todo = (
            BASIC,
            self.commit_author,
            self.version_variable,
            self.changelog_file,
            self.changelog_header,
            self.gitea_token_var,
            self.commit_message,
            '',
        )
        result = baw.NEWLINE.join(todo)
        return result


BASIC = """\
[semantic_release]
commit_changelog=True
commit_subject={version} auto generated release
version_source=commit
parser_angular_patch_types=fix,perf,chore
changelog_sections=feature,fix,breaking,documentation,performance,chore
changelog_components=baw.changelog.changelog_headers
upload_to_repository=true
upload_to_pypi=false
upload_to_release=false

hvcs=gitea
"""


def determine_changelog(root: str, verbose: bool, venv: bool = False) -> str:
    cmd = 'baw_semantic_release changelog '
    cmd += version_variables(root)
    cmd += '-D "changelog_components=baw.changelog.changelog_headers" '
    cmd += '-D "branches=prod main master" '
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
    if not baw.gix.headhash(root):
        return True
    return False
