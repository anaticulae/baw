# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import sys

import baw.config
import baw.utils


def cov_args(
    root: str,
    *,
    pdb: bool,
    outdir: str = None,
    report: bool = True,
) -> str:
    """Determine args for running tests based on project-root.

    Args:
        root(str): project root
        pdb(bool): using debugger on running tests
        outdir(str): if str, write to outdir; if not, use default
        report(bool): generate html report
    Returns:
        args for coverage cmd
    """
    output = os.path.join(baw.utils.tmp(root), 'report')
    if isinstance(outdir, str):
        output = baw.utils.fixup_windows(outdir)
    cov_config = os.path.join(baw.ROOT, 'baw/templates', '.coveragerc')
    assert os.path.exists(cov_config), str(cov_config)
    no_cov = '--no-cov ' if pdb else ''
    if no_cov:
        baw.utils.log('Disable coverage report')
    min_cov = baw.config.coverage_min(root)
    cov_sources = collect_cov_sources(root)
    cov = (f'-p pytest_cov --cov-config={cov_config} {cov_sources} '
           f'--cov-branch {no_cov} '
           f'--cov-fail-under={min_cov} ')
    if report:
        cov += f'--cov-report=html:{output} '
    cov = cov.strip()
    return cov


def collect_cov_sources(root: str) -> str:
    """Collect source code folder from project configuration.

    Args:
        root(str): path to project root
    Returns:
        list of --cov= collected from `source` cfg
    """
    project_sources = baw.config.sources(root)
    ret = 0
    cov_sources = ''
    for item in project_sources:
        code_path = os.path.join(root, item)
        if not os.path.exists(code_path):
            msg = f'path {code_path} from `project.cfg` does not exist'
            baw.utils.error(msg)
            ret += 1
            continue
        cov_sources += f'--cov={code_path} '
    if ret:
        sys.exit(ret)
    return cov_sources


NOT_SELECTED = 'NOT_SELECTED'


def select_cov(args):
    """Select optional cov path or default one, or no cov.

    --cov
    >>> select_cov(dict(cov=None))
    True

    --cov=/var/workdir
    >>> select_cov(dict(cov='/var/workdir'))
    '/var/workdir'

    >>> select_cov(dict(cov=NOT_SELECTED))
    False
    """
    if args['cov'] == NOT_SELECTED:
        return False
    if args['cov']:
        # --cov=/var/workdir
        return args['cov']
    # --cov without data
    return True
