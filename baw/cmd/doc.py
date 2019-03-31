#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
from os.path import join

from baw.config import name as project_name
from baw.config import shortcut
from baw.resources import DOC_CONF
from baw.resources import template_replace
from baw.runtime import run_target
from baw.utils import file_replace
from baw.utils import logging


def update_template(root: str, virtual: bool = False):
    path = join(root, 'docs/conf.py')
    replaced = template_replace(root, DOC_CONF)

    file_replace(path, replaced)


def doc(root: str, virtual: bool = False):
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
    update_template(root, virtual=virtual)

    docs = join(root, 'docs')
    html = join(docs, 'html')
    tmp = join(docs, '.tmp')
    sources = root  # include test and package
    ignore = [
        'templates',
        'setup.py',
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
    completed = run_target(root, command=command, cwd=root, virtual=virtual)

    if completed.returncode:
        return completed.returncode

    # Create html result
    logging('Make html')
    build_options = [
        # '-vvvv ',
        # '-n',  # warn about all missing references
        # '-W',  # turn warning into error
        # '-b coverage',  # TODO: Check autodoc package
        '-j 8'
    ]
    build_options = ' '.join(build_options)

    command = 'sphinx-build -M html %s %s %s'
    command = command % (docs, docs, build_options)

    result = run_target(root, command, virtual=virtual)
    return result.returncode
