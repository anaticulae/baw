###############################################################################
#                                Kiwi Project                                 #
#                                    2019                                     #
#                          Helmut Konrad Fahrendholz                          #
#                             kiwi@derspanier.de                              #
###############################################################################
from functools import partial
from os import environ
from os.path import exists
from os.path import join

from baw.config import minimal_coverage
from baw.config import shortcut
from baw.runtime import git_stash
from baw.runtime import run_target
from baw.utils import check_root
from baw.utils import logging
from baw.utils import logging_error
from baw.utils import ROOT
from baw.utils import tmp

# pytest returncode when runnining without tests
# from _pytest.main import EXIT_NOTESTSCOLLECTED


def test(
        root: str,
        *,
        coverage: bool = False,
        fast: bool = False,
        longrun: bool = False,
        pdb: bool = False,
        stash: bool = False,
        verbose: bool = False,
        virtual: bool = False,
):
    """Running test-step in root/tests

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
        exit(1)

    env = dict(environ.items())
    if longrun:
        env['LONGRUN'] = 'True'  # FAST = 'LONGRUN' not in environ.keys()
    if fast:
        env['FAST'] = 'True'  # Skip all tests wich are long or medium

    debugger = '--pdb ' if pdb else ''
    cov = cov_args(root, pdb=debugger) if coverage else ''
    log_file = join(tmp(root), 'tests.log')
    # using ROOT to get location from baw-tool
    test_config = join(ROOT, 'templates', 'pytest.ini')
    assert exists(test_config)

    cmd = ('pytest -c %s %s %s --log-file="%s" %s') % (
        test_config,
        debugger,
        cov,
        log_file,
        test_dir,
    )

    skip_error = {NO_TEST_TO_RUN}  # no pytest available = no problem
    target = partial(
        run_target,
        root,
        cmd,
        cwd=test_dir,
        debugging=pdb,
        env=env,
        verbose=verbose,
        skip_error=skip_error,
        virtual=virtual,
    )
    stash = False

    if stash:
        with git_stash(root, virtual):
            completed = target()
    else:
        completed = target()
    returncode = completed.returncode

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

    short = shortcut(root)
    source = join(root, short)
    tests = join(root, 'tests')
    output = join(tmp(root), 'report')
    cov_config = join(ROOT, 'templates', '.coveragerc')
    assert exists(cov_config)

    #   --no-cov  Disable coverage report completely (useful for
    #             debuggers) default: False
    no_cov = '--no-cov ' if pdb else ''
    if no_cov:
        logging('Disable coverage report')

    min_cov = minimal_coverage(root)
    cov = ('--cov-config="%s" --cov="%s" --cov-report=html:%s --cov-branch'
           ' %s --cov-fail-under=%d') % (
               cov_config,
               source,
               output,
               no_cov,
               min_cov,
           )
    return cov
