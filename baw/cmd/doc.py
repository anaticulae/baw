#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
import os
import webbrowser

import baw.utils
from baw.resources import DOC_CONF
from baw.resources import template_replace
from baw.runtime import run_target
from baw.utils import TMP
from baw.utils import file_replace
from baw.utils import logging


def doc(root: str, virtual: bool = False, verbose: bool = False) -> int:
    """Run Sphinx doc generation

    The result is locatated in `doc/html` as html-report. The stderr and
    stdout are printed to console.

    Args:
        root(str): project root
        virtual(bool): run in virtual environment
        verbose(bool): if True more logging information are provided
    Returns:
        0 if generation was successful
        1 if some errors occurs
    """
    if not is_sphinx_installed(root=root, virtual=virtual):
        msg = 'sphinx is not installed, run baw --sync=all --virtual'
        baw.utils.logging_error(msg)
        return baw.utils.FAILURE

    update_template(root)

    docs = os.path.join(root, 'docs')
    tmp = os.path.join(docs, TMP)

    sources = root  # include test and package
    ignore = ' '.join([
        'templates',
        'setup.py',
        'conf.py',
    ])

    # Create files out of source
    # -d maxdepth
    # -M modules first
    # -f overwrite existing files
    # -e put each module on its own page
    configuration = '-d 10 -M -f -e'
    command = 'sphinx-apidoc %s -o %s %s %s'
    command = command % (configuration, tmp, sources, ignore)

    logging('generate docs')
    if verbose:
        logging(command)

    completed = run_target(
        root,
        command=command,
        cwd=root,
        verbose=verbose,
        virtual=virtual,
    )
    if completed.returncode:
        return completed.returncode

    # Create html result
    build_options = ' '.join([
        # '-vvvv ',
        '-n',  # warn about all missing references
        '-W',  # turn warning into error
        '--keep-going',
        # '-b coverage',  # TODO: Check autodoc package
        '-j 8'
    ])

    htmloutput = os.path.join(docs, 'html')
    command = f'sphinx-build {docs} {htmloutput} {build_options}'

    logging('make html')
    if verbose:
        logging(command)

    result = run_target(
        root,
        command=command,
        cwd=root,
        virtual=virtual,
        verbose=verbose,
    )
    if 'PYTEST_CURRENT_TEST' in os.environ:
        # running with pytest do not open webbrowser
        return result.returncode

    if result.returncode == baw.utils.SUCCESS:
        url = os.path.join(htmloutput, 'index.html')
        webbrowser.open_new(url)

    return result.returncode


def update_template(root: str):
    path = os.path.join(root, 'docs/conf.py')
    replaced = template_replace(root, DOC_CONF)

    file_replace(path, replaced)


def is_sphinx_installed(root: str, virtual: bool) -> bool:
    """Use `pip` to verify that documentation tool `sphinx` is installed."""
    command = 'pip show sphinx'
    completed = run_target(
        root,
        command=command,
        cwd=root,
        virtual=virtual,
        skip_error_code=[1],  # sphinx is not installed
        verbose=False,
    )
    isinstalled = completed.returncode == baw.utils.SUCCESS
    return isinstalled
