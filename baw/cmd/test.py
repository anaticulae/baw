# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
from functools import partial
from os import environ
from os.path import exists
from os.path import join

from baw.config import minimal_coverage
from baw.config import shortcut
from baw.config import sources
from baw.runtime import git_stash
from baw.runtime import run_target
from baw.utils import FAILURE
from baw.utils import ROOT
from baw.utils import check_root
from baw.utils import logging
from baw.utils import logging_error
from baw.utils import remove_tree
from baw.utils import tmp

# pytest returncode when runnining without tests
# from _pytest.main import EXIT_NOTESTSCOLLECTED
NO_TEST_TO_RUN = 5


def run_test(
        root: str,
        *,
        coverage: bool = False,
        fast: bool = False,
        longrun: bool = False,
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
    test_dir = join(root, 'tests')
    if not exists(test_dir):
        logging_error('No testdirectory %s available' % test_dir)
        exit(FAILURE)

    env = dict(environ.items())
    if longrun:
        env['LONGRUN'] = 'True'  # FAST = 'LONGRUN' not in environ.keys()
    if fast:
        env['FAST'] = 'True'  # Skip all tests wich are long or medium

    debugger = '--pdb ' if pdb else ''
    cov = cov_args(root, pdb=debugger) if coverage else ''
    tmp_path = tmp(root)
    tmp_test_path = join(tmp_path, 'test')

    if exists(tmp_test_path):
        remove_tree(tmp_test_path)

    log_file = join(tmp_path, 'tests.log')
    # using ROOT to get location from baw-tool
    test_config = join(ROOT, 'templates', 'pytest.ini')
    assert exists(test_config), 'No testconfig available %s' % test_config

    override_testconfig = '--verbose --durations=10'
    if quiet:
        override_testconfig = '--quiet'

    # python -m to include sys path of cwd
    # --basetemp define temp directory where the tests run
    cmd = 'python -m pytest -c %s %s %s %s --basetemp=%s --log-file="%s" %s'
    cmd = cmd % (
        test_config,
        override_testconfig,
        debugger,
        cov,
        tmp_test_path,
        log_file,
        test_dir,
    )

    skip_error_code = {NO_TEST_TO_RUN}  # no pytest available = no problem
    target = partial(
        run_target,
        root,
        cmd,
        cwd=root,  # to include project code(namespace) into syspath
        debugging=pdb,
        env=env,
        verbose=verbose,
        skip_error_code=skip_error_code,
        virtual=virtual,
    )

    if stash:
        with git_stash(root, verbose=verbose, virtual=virtual):
            completed = target()
    else:
        completed = target()
    returncode = completed.returncode

    # Print output of test run
    logging(completed.stdout)
    if returncode == NO_TEST_TO_RUN:
        return 0

    return returncode


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
            logging_error('Path %s in `projet.cfg` does not exist')
            ret += 1
            continue
        cov_sources += '--cov=%s ' % code_path
    if ret:
        exit(ret)
    return cov_sources
