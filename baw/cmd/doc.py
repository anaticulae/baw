#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os
import shutil

import baw.config
import baw.resources
import baw.runtime
import baw.utils


def doc(root: str, venv: bool = False, verbose: bool = False) -> int:
    """Run Sphinx doc generation

    The result is locatated in `doc/html` as html-report. The stderr and
    stdout are printed to console.

    Args:
        root(str): project root
        venv(bool): run in venv environment
        verbose(bool): if True more logging information are provided
    Returns:
        0 if generation was successful
        1 if some errors occurs
    """
    if not is_sphinx_installed(root=root, venv=venv):
        msg = 'sphinx is not installed, run baw sync=all --venv'
        baw.utils.error(msg)
        return baw.utils.FAILURE
    if returnvalue := generate_docs(root, verbose, venv):
        return returnvalue
    if returnvalue := build_html(root, verbose, venv):
        return returnvalue
    open_docs(root)
    return baw.utils.SUCCESS


def generate_docs(root: str, verbose: bool, venv: bool) -> int:
    doctmp = baw.config.docpath(root)
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
    cmd = 'sphinx-apidoc %s -o %s %s %s'
    cmd = cmd % (configuration, doctmp, sources, ignore)
    baw.utils.log('generate docs')
    if verbose:
        baw.utils.log(cmd)
    completed = baw.runtime.run_target(
        root,
        cmd=cmd,
        cwd=root,
        verbose=verbose,
        venv=venv,
    )
    if completed.returncode:
        return completed.returncode
    path = os.path.join(baw.config.docpath(root), 'conf.py')
    replaced = baw.resources.template_replace(root, baw.resources.DOC_CONF)
    baw.utils.file_replace(path, replaced)
    doctmp = baw.config.docpath(root)
    # copy docs
    baw.utils.log('sync docs')
    source = os.path.join(root, 'docs')
    shutil.copytree(source, doctmp, dirs_exist_ok=True)
    for filename in 'CHANGELOG.md'.split():
        path = os.path.join(root, filename)
        if not os.path.exists(path):
            continue
        loaded = baw.utils.file_read(path)
        baw.utils.file_replace(os.path.join(doctmp, filename), loaded)
    for filename in 'changelog.rst'.split():
        path = os.path.join(doctmp, 'pages', filename)
        if not os.path.exists(path):
            continue
        loaded = baw.utils.file_read(path)
        loaded = loaded.replace('../../', '../')
        baw.utils.file_replace(path, loaded)
    return baw.utils.SUCCESS


def build_html(root: str, verbose: bool, venv: bool) -> int:
    # Create html result
    build_options = ' '.join([
        # '-vvvv ',
        '-n',  # warn about all missing references
        '-W',  # turn warning into error
        '--keep-going',
        # '-b coverage',  # TODO: Check autodoc package
        '-j 8'
    ])
    doctmp = baw.config.docpath(root)
    htmloutput = os.path.join(doctmp, 'html')
    cmd = f'sphinx-build {doctmp} {htmloutput} {build_options}'
    baw.utils.log('make html')
    if verbose:
        baw.utils.log(cmd)
    result = baw.runtime.run_target(
        root,
        cmd=cmd,
        cwd=root,
        venv=venv,
        verbose=verbose,
    )
    return result.returncode


def update_template(root: str):
    path = os.path.join(baw.config.docpath(root), 'conf.py')
    replaced = baw.resources.template_replace(root, baw.resources.DOC_CONF)
    baw.utils.file_replace(path, replaced)


def open_docs(root: str):
    doctmp = baw.config.docpath(root)
    htmloutput = os.path.join(doctmp, 'html')
    url = os.path.join(htmloutput, 'index.html')
    baw.utils.openbrowser(url)


def is_sphinx_installed(root: str, venv: bool) -> bool:
    """Use `pip` to verify that documentation tool `sphinx` is installed."""
    cmd = 'pip show sphinx'
    completed = baw.runtime.run_target(
        root,
        cmd=cmd,
        cwd=root,
        venv=venv,
        skip_error_code=[1],  # sphinx is not installed
        verbose=False,
    )
    isinstalled = completed.returncode == baw.utils.SUCCESS
    return isinstalled


def extend_cli(parser):
    lints = parser.add_parser('doc', help='Generate docs using Sphinx')
    lints.set_defaults(func=baw.run.run_doc)
