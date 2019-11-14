# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
from functools import partial
from os import environ
from os.path import exists
from os.path import join
from shutil import rmtree
from webbrowser import open_new

from baw.config import minimal_coverage
from baw.config import sources
from baw.datetime import current
from baw.git import git_stash
from baw.runtime import run_target
from baw.utils import FAILURE
from baw.utils import ROOT
from baw.utils import SUCCESS
from baw.utils import check_root
from baw.utils import logging
from baw.utils import logging_error
from baw.utils import tmp

# pytest returncode when runnining without tests
# from _pytest.main import EXIT_NOTESTSCOLLECTED
NO_TEST_TO_RUN = 5


def run_test(
        root: str,
        testconfig=None,
        *,
        coverage: bool = False,
        fast: bool = False,
        generate: bool = False,
        longrun: bool = False,
        nightly: bool = False,
        pdb: bool = False,
        quiet: bool = False,
        stash: bool = False,
        verbose: bool = False,
        virtual: bool = False,
):
    """Running test-step in root/tests

    Hint:
        The tests run in `root` to include namespace of project code.
    Args:
        longrun(bool): Runnig all tests
        pdf(bool): Run debugger on error
        stash(bool): Stash all changes to test commited-change in repository
        virtual(bool): run command in virtual environment
    Returns:
        returncode(int): 0 if successful else > 0

    """
    check_root(root)

    logging('Running tests')
    testdir, testenv = setup_testenvironment(
        root,
        fast=fast,
        longrun=longrun,
        nightly=nightly,
        generate=generate,
    )

    generate_only = generate and not (fast or longrun or nightly)

    cmd = test_run_command(
        root,
        testdir,
        pdb,
        coverage,
        quiet,
        testconfig,
        generate_only=generate_only,
    )
    target = partial(
        run_target,
        root,
        cmd,
        cwd=root,  # to include project code(namespace) into syspath
        debugging=True,  # live test reporting
        env=testenv,
        verbose=verbose,
        skip_error_code={NO_TEST_TO_RUN},  # no tests available => no problem
        virtual=virtual,
    )

    if stash:
        with git_stash(root, verbose=verbose, virtual=virtual):
            completed = target()
    else:
        completed = target()
    if generate_only and completed.returncode == SUCCESS:
        # do not write log of collect tests
        logging('test data generated')

    if completed.returncode == NO_TEST_TO_RUN:
        return SUCCESS
    if completed.returncode == SUCCESS and coverage:
        open_report(root)
    return completed.returncode


def open_report(root: str):
    """Open test coverage report after successful test-run"""
    url = join(tmp(root), 'report/index.html')
    open_new(url)


def setup_testenvironment(
        root: str,
        fast: bool,
        longrun: bool,
        nightly: bool,
        generate: bool,
):
    testdir = join(root, 'tests')
    if not exists(testdir):
        logging_error('No testdirectory %s available' % testdir)
        exit(FAILURE)

    env = dict(environ.items())
    if longrun:
        env['LONGRUN'] = 'True'  # FAST = 'LONGRUN' not in environ.keys()
    if fast:
        env['FAST'] = 'True'  # Skip all tests wich are long or medium
    if nightly:
        env['NIGHTLY'] = 'True'  # Very long running test
    if generate:
        env['GENERATE'] = 'True'  # Generate test resources

    # comma-separated plugins to load during startup
    env['PYTEST_PLUGINS'] = 'pytester'

    return testdir, env


PYTEST_INI = join(ROOT, 'templates/pytest.ini')


def test_run_command(
        root,
        test_dir,
        pdb,
        coverage,
        quiet,
        parameter,
        generate_only,
):
    # using ROOT to get location from baw-tool
    assert exists(PYTEST_INI), 'No testconfig available %s' % PYTEST_INI

    debugger = '--pdb ' if pdb else ''
    cov = cov_args(root, pdb=debugger) if coverage else ''

    tmp_ = tmp(root)
    tmp_testpath = join(tmp_, 'test_%s' % current(seconds=True, separator='_'))
    if exists(tmp_testpath):
        # remove test folder if exists
        rmtree(tmp_testpath)
    override_testconfig = '--quiet' if quiet else '--verbose --durations=10'

    manual_parameter = ' '.join(parameter) if parameter else ''
    manual_parameter = manual_parameter.replace('+', '-')

    generate_only = '--collect-only' if generate_only else ''
    # python -m to include sys path of cwd
    # --basetemp define temp directory where the tests run
    cmd = 'python -m pytest -c %s %s %s %s %s %s --basetemp=%s %s'
    cmd = cmd % (
        PYTEST_INI,
        manual_parameter,
        override_testconfig,
        debugger,
        cov,
        generate_only,
        tmp_testpath,
        test_dir,
    )
    return cmd


def cov_args(root: str, *, pdb: bool):
    """Determine args for running tests based on project-root

    Args:
        root(str): project root
        pdb(bool): using debugger on running tests

    Returns:
        args for coverage command
    """
    output = join(tmp(root), 'report')
    cov_config = join(ROOT, 'templates', '.coveragerc')
    assert exists(cov_config)

    #   --no-cov  Disable coverage report completely (useful for
    #             debuggers) default: False
    no_cov = '--no-cov ' if pdb else ''
    if no_cov:
        logging('Disable coverage report')

    min_cov = minimal_coverage(root)

    cov_sources = collect_cov_sources(root)
    cov = ('--cov-config=%s %s --cov-report=html:%s --cov-branch'
           ' %s --cov-fail-under=%d') % (
               cov_config,
               cov_sources,
               output,
               no_cov,
               min_cov,
           )
    return cov


def collect_cov_sources(root: str):
    """Collect source code folder from project configuration

    Args:
        root(str): path to project root
    Returns:
        list of --cov= collected from `source` cfg
    """
    project_sources = sources(root)
    ret = 0
    cov_sources = ''
    for item in project_sources:
        code_path = join(root, item)
        if not exists(code_path):
            msg = 'Path %s from `project.cfg` does not exist' % code_path
            logging_error(msg)
            ret += 1
            continue
        cov_sources += '--cov=%s ' % code_path
    if ret:
        exit(ret)
    return cov_sources
