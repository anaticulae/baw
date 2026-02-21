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
import baw.utils

AUTOMATED = 'Automated Release <automated_release@ostia.la>'

TEMPLATE = baw.utils.file_read(os.path.join(baw.ROOT, 'baw/templates/semantic.cfg')) # yapf:disable


@contextlib.contextmanager
def temp_semantic_config(root: str, verbose: bool, venv: bool = False):
    generated = TEMPLATE.replace('{{REPO_DIR}}', root)
    # use own tmpfile cause TemporaryFile(delete=True) seems no supported
    # at linux, parameter delete is missing.
    config = os.path.join(root, 'setup.cfg')
    baw.utils.file_create(config, generated)
    yield config
    # remove file
    os.unlink(config)


def version_variables(root: str) -> str:
    short = baw.config.version(root)
    result = f'-D "version_variable={short}" '
    return result


def firstversion(root: str) -> bool:
    if not baw.gix.headhash(root):
        return True
    return False
