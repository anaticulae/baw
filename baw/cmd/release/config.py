# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import os

import baw.config
import baw.gix
import baw.utils

TEMPLATES = os.path.join(baw.ROOT, 'baw/templates')
TEMPLATE = baw.utils.file_read(os.path.join(TEMPLATES, 'semantic.cfg'))
SEMANTIC = os.path.join(TEMPLATES, 'semantic')


@contextlib.contextmanager
def release_config_tmp(root: str, verbose: bool):
    package = baw.config.shortcut(root)
    generated = TEMPLATE + ''
    generated = generated.replace('{{REPO_DIR}}', root)
    generated = generated.replace('{{PACKAGE}}', package)
    generated = generated.replace('{{TEMPLATE_DIR}}', SEMANTIC)
    generated = generated.replace(
        '{{UPLOAD_TO_VCS_RELEASE}}',
        str(is_ci()).lower(),
    )
    if verbose:
        baw.utils.log(generated)
    # use own tmpfile cause TemporaryFile(delete=True) seems no supported
    # at linux, parameter delete is missing.
    config = configpath(root)
    baw.utils.file_replace(config, generated)
    yield config
    # remove file
    os.unlink(config)


def firstversion(root: str) -> bool:
    if not baw.gix.headhash(root):
        return True
    return False


def configpath(root: str):
    tmp = baw.utils.tmp(root)
    config = os.path.join(
        tmp,
        'release.cfg',
    )
    return config


def is_ci() -> bool:
    # jenkins or github
    ci = os.environ.get('JENKINS_HOME', False) or os.environ.get('CI', False)
    result = bool(ci)
    return result
