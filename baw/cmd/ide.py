# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""The purpose of this module is to setup the development environment of the
user and start the ide afterwards. """
from os.path import join

from baw.resources import CODE_WORKSPACE as TEMPLATE
from baw.resources import ISORT_TEMPLATE
from baw.resources import RCFILE_PATH
from baw.resources import template_replace
from baw.runtime import run_target
from baw.utils import file_replace
from baw.utils import forward_slash
from baw.utils import logging
from baw.utils import tmp

WORKSPACE_NAME = '..code-workspace'


def ide_open(root: str):
    """Generate vscode workspace and run afterwards"""
    logging('generate')
    generate_workspace(root)
    generate_sort_config(root)
    logging('open')
    completed = start(root)
    return completed


def generate_workspace(root: str):
    output = workspace_configuration(root)
    rcfile = forward_slash(RCFILE_PATH)
    isortfile = sort_configuration(root)

    replaced = template_replace(root, TEMPLATE, rcfile=rcfile, isort=isortfile)

    file_replace(output, replaced)


def generate_sort_config(root: str):
    output = sort_configuration(root)
    replaced = template_replace(root, ISORT_TEMPLATE)
    file_replace(output, replaced)


def start(root):
    output = workspace_configuration(root)
    cmd = 'code %s &' % output
    completed = run_target(root, cmd, verbose=False)
    return completed.returncode


def sort_configuration(root: str):
    return forward_slash(join(tmp(root), '.isort.cfg'))


def workspace_configuration(root: str):
    """Path to generated workspace configuration"""
    return forward_slash(join(root, '..code-workspace'))
