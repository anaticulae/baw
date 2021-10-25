# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import shutil
import sys

import baw.archive.test
import baw.config
import baw.datetime
import baw.git
import baw.runtime
import baw.utils

# pytest returncode when runnining without tests
# from _pytest.main import EXIT_NOTESTSCOLLECTED
NO_TEST_TO_RUN = 5


def run_test(  # pylint:disable=R0914
    root: str,
    testconfig: list = None,
    *,
    coverage: bool = False,
    fast: bool = False,
    generate: bool = False,
    instafail: bool = False,
    longrun: bool = False,
    nightly: bool = False,
    pdb: bool = False,
    quiet: bool = False,
    stash: bool = False,
    verbose: bool = False,
    virtual: bool = False,
) -> int:
    """Running test-step in root/tests

    Hint:
        The tests run in `root` to include namespace of project code.
    Args:
        root(str): path to root of tested project
        testconfig(list): list of user defined test parameter via -k
        coverage(bool): run python test coverage
        fast(bool): skip long running tests
        generate(bool): generate required test data
        instafail(bool): print error while running pytest
        longrun(bool): run long running tests
        nightly(bool): run all tests
        pdb(bool): run debugger on error
        quiet(bool): pytest - use minimal logging
        stash(bool): stash all changes to test commited-change in repository
        verbose(bool): extend logging
        virtual(bool): run command in virtual environment
    Returns:
        returncode(int): 0 if successful else > 0
    """
    if not any((generate, nightly, longrun, fast)):
        baw.utils.log('skip tests...')
        return baw.utils.SUCCESS
    baw.utils.check_root(root)

    baw.utils.log('tests')
    _, testenv = setup_testenvironment(
        root,
        fast=fast,
        longrun=longrun,
        nightly=nightly,
        generate=generate,
    )

    generate_only = generate and not (fast or longrun or nightly)

    cmd = create_test_cmd(
        root,
        coverage=coverage,
        generate_only=generate_only,
        instafail=instafail,
        parameter=testconfig,
        pdb=pdb,
        quiet=quiet,
        verbose=verbose,
        virtual=virtual,
    )

    environment = baw.git.git_stash if stash else baw.utils.empty
    with environment(root, verbose=verbose, virtual=virtual):
        completed = baw.runtime.run_target(
            root,
            cmd,
            cwd=root,  # to include project code(namespace) into syspath
            debugging=True,  # live test reporting
            env=testenv,
            verbose=verbose,
            # no tests available => no problem
            skip_error_code={NO_TEST_TO_RUN},
            virtual=virtual,
        )

    if completed.returncode == baw.utils.SUCCESS:
        if generate_only:
            # do not write log of collect tests
            baw.utils.log('test data generated')
        if coverage:
            open_report(root)
        # do not log partial long running tests as completed
        # TODO: ADJUST -n6!!!
        # TODO: VERIFY THAT SELECTIVE TESTING WAS NOT USED
        if all_tests(testconfig) and (longrun or nightly):
            head = baw.git.git_headhash(root)
            if head:
                baw.archive.test.mark_tested(root, head)
    if completed.returncode == NO_TEST_TO_RUN:
        # override pytest error code
        return baw.utils.SUCCESS
    return completed.returncode


def all_tests(testconfig) -> bool:
    if not testconfig:
        return True
    if 'pyargs' in str(testconfig):
        return False
    if '-k' not in str(testconfig):
        return True
    return False


def open_report(root: str):
    """Open test coverage report after successful test-run"""
    url = os.path.join(baw.utils.tmp(root), 'report/index.html')
    baw.utils.openbrowser(url)


def setup_testenvironment(
    root: str,
    fast: bool,
    longrun: bool,
    nightly: bool,
    generate: bool,
):
    testdir = os.path.join(root, 'tests')
    if not os.path.exists(testdir):
        baw.utils.error('No testdirectory %s available' % testdir)
        sys.exit(baw.utils.FAILURE)
    env = dict(os.environ.items())
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


def create_test_cmd(  # pylint:disable=R0914
    root,
    *,
    instafail,
    pdb,
    coverage,
    quiet,
    parameter,
    generate_only,
    verbose: bool = False,
    virtual: bool = False,
):
    pytest_ini = os.path.join(baw.ROOT, 'baw/templates/pytest.ini')
    # using ROOT to get location from baw-tool
    assert os.path.exists(pytest_ini), f'no testconfig available {pytest_ini}'
    # configure test run
    debugger = '--pdb ' if pdb else ''
    cov = cov_args(root, pdb=debugger) if coverage else ''
    # create test directory
    tmp_testpath, cachedir = create_testdir(root)
    # config
    override_testconfig = '--quiet' if quiet else '--verbose --durations=10'
    manual_parameter = ' '.join(parameter) if parameter else ''
    manual_parameter = manual_parameter.replace('+', '-')
    if '-n' in manual_parameter:
        manual_parameter = f'-p xdist {manual_parameter}'
    generate_only = '--collect-only' if generate_only else ''
    sources = tests_sources(root, parameter)
    # python -m to include sys path of cwd
    # --basetemp define temp directory where the tests run
    # run pytest
    python = baw.config.python(root, virtual=virtual)
    cmd = (f'{python} -m pytest -c {pytest_ini} {manual_parameter} '
           f'{override_testconfig} {debugger} {cov} {generate_only} '
           f'--basetemp={tmp_testpath} '
           f'-o cache_dir={cachedir} {sources}')
    if instafail:
        cmd += '--instafail '
    if verbose:
        cmd += '-vv '
    return cmd


def create_testdir(root):
    tmpdir = baw.utils.tmp(root)
    testtime = baw.datetime.current(seconds=True, separator='_')
    testfolder = f'test_{testtime}'
    logfolder = os.path.join(tmpdir, 'log')
    os.makedirs(logfolder, exist_ok=True)
    tmp_testpath = os.path.join(tmpdir, testfolder)
    if os.path.exists(tmp_testpath):
        # remove test folder if exists
        shutil.rmtree(tmp_testpath)
    cachedir = os.path.join(tmpdir, 'pytest_cache')
    return tmp_testpath, cachedir


def tests_sources(root, parameter) -> str:
    # set to root to run doctests for all subproject's
    testdir = os.path.join(root, 'tests')
    doctests = ' '.join(baw.config.sources(root))
    if 'pyargs' in str(parameter):
        # select tests by --pyargs
        testdir, doctests = '', ''
    result = f'{testdir} {doctests} '
    return result


def cov_args(root: str, *, pdb: bool) -> str:
    """Determine args for running tests based on project-root.

    Args:
        root(str): project root
        pdb(bool): using debugger on running tests
    Returns:
        args for coverage command
    """
    output = os.path.join(baw.utils.tmp(root), 'report')
    cov_config = os.path.join(baw.ROOT, 'baw/templates', '.coveragerc')
    assert os.path.exists(cov_config), str(cov_config)
    no_cov = '--no-cov ' if pdb else ''
    if no_cov:
        baw.utils.log('Disable coverage report')
    min_cov = baw.config.minimal_coverage(root)
    cov_sources = collect_cov_sources(root)
    cov = (f'--cov-config={cov_config} {cov_sources} '
           f'--cov-report=html:{output} --cov-branch {no_cov} '
           f'--cov-fail-under={min_cov}')
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
