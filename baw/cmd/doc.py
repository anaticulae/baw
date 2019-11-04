#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
import os
import webbrowser
from os.path import join

import baw.utils
from baw.resources import DOC_CONF
from baw.resources import template_replace
from baw.runtime import run_target
from baw.utils import TMP
from baw.utils import file_replace
from baw.utils import logging


def update_template(root: str):
    path = join(root, 'docs/conf.py')
    replaced = template_replace(root, DOC_CONF)

    file_replace(path, replaced)


def doc(root: str, virtual: bool = False, verbose: bool = False):
    """Run Sphinx doc generation

    The result is locatated in `doc/html` as html-report. The stderr and
    stdout are printed to console.

    Args:
        root(str): project root
        virtual(bool): run in virtual environment
    Returns:
        0 if generation was sucessful
        1 if some errors occurs
     """
    update_template(root)

    docs = join(root, 'docs')
    tmp = join(docs, TMP)

    sources = root  # include test and package
    ignore = [
        'templates',
        'setup.py',
        'conf.py',
    ]
    ignore = ' '.join(ignore)

    # Create files out of source
    # -d maxdepth
    # -M modules first
    # -f overwrite existing files
    # -e put each module on its own page
    configuration = '-d 10 -M -f -e'
    command = 'sphinx-apidoc %s -o %s %s %s'
    command = command % (configuration, tmp, sources, ignore)

    logging('generate docs')
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
    build_options = [
        # '-vvvv ',
        # '-n',  # warn about all missing references
        # '-W',  # turn warning into error
        # '-b coverage',  # TODO: Check autodoc package
        '-j 8'
    ]
    build_options = ' '.join(build_options)

    htmloutput = os.path.join(docs, 'html')
    command = f'sphinx-build {docs} {htmloutput} {build_options}'

    logging('make html')
    logging(command)

    result = run_target(
        root,
        command=command,
        cwd=root,
        virtual=virtual,
        verbose=verbose,
    )
    if result.returncode == baw.utils.SUCCESS:
        url = os.path.join(htmloutput, 'index.html')
        webbrowser.open_new(url)
    return result.returncode
