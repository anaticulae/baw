# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import shutil

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
    baw.utils.check_root(root)

    baw.utils.logging('tests')
    testdir, testenv = setup_testenvironment(
        root,
        fast=fast,
        longrun=longrun,
        nightly=nightly,
        generate=generate,
    )

    generate_only = generate and not (fast or longrun or nightly)

    cmd = create_test_cmd(
        root,
        testdir,
        pdb,
        coverage,
        quiet,
        testconfig,
        generate_only=generate_only,
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
            baw.utils.logging('test data generated')
        if coverage:
            open_report(root)
        # do not log partial long running tests as completed
        complete = (not testconfig) or (testconfig == ['+n=auto'])
        if complete and (longrun or nightly):
            head = baw.git.git_headhash(root)
            if head:
                baw.archive.test.mark_tested(root, head)
    if completed.returncode == NO_TEST_TO_RUN:
        # override pytest error code
        return baw.utils.SUCCESS
    return completed.returncode


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
        baw.utils.logging_error('No testdirectory %s available' % testdir)
        exit(baw.utils.FAILURE)

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


PYTEST_INI = os.path.join(baw.utils.ROOT, 'templates/pytest.ini')


def create_test_cmd(  # pylint:disable=R0914
        root,
        testdir,  # TODO: REMOVE?
        pdb,
        coverage,
        quiet,
        parameter,
        generate_only,
):
    # using ROOT to get location from baw-tool
    assert os.path.exists(PYTEST_INI), 'No testconfig available %s' % PYTEST_INI

    debugger = '--pdb ' if pdb else ''
    cov = cov_args(root, pdb=debugger) if coverage else ''

    tmpdir = baw.utils.tmp(root)
    testfolder = 'test_%s' % baw.datetime.current(seconds=True, separator='_')
    tmp_testpath = os.path.join(tmpdir, testfolder)
    if os.path.exists(tmp_testpath):
        # remove test folder if exists
        shutil.rmtree(tmp_testpath)
    override_testconfig = '--quiet' if quiet else '--verbose --durations=10'

    manual_parameter = ' '.join(parameter) if parameter else ''
    manual_parameter = manual_parameter.replace('+', '-')

    generate_only = '--collect-only' if generate_only else ''

    # set to root to run doctests for all subproject's
    testdir = str(os.path.join(root, 'tests'))

    doctests = ' '.join(baw.config.sources(root))
    # python -m to include sys path of cwd
    # --basetemp define temp directory where the tests run
    cachedir = os.path.join(tmpdir, 'pytest_cache')

    testlog = os.path.join(tmpdir, f'{testfolder}.log')

    cmd = (f'python -m pytest -c {PYTEST_INI} {manual_parameter} '
           f'{override_testconfig} {debugger} {cov} {generate_only} '
           f'--basetemp={tmp_testpath} '
           f'-o cache_dir={cachedir} {testdir} {doctests} | tee {testlog}')
    return cmd


def cov_args(root: str, *, pdb: bool) -> str:
    """Determine args for running tests based on project-root.

    Args:
        root(str): project root
        pdb(bool): using debugger on running tests

    Returns:
        args for coverage command
    """
    output = os.path.join(baw.utils.tmp(root), 'report')
    cov_config = os.path.join(baw.utils.ROOT, 'templates', '.coveragerc')
    assert os.path.exists(cov_config)

    #   --no-cov  Disable coverage report completely (useful for
    #             debuggers) default: False
    no_cov = '--no-cov ' if pdb else ''
    if no_cov:
        baw.utils.logging('Disable coverage report')

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
            msg = 'Path %s from `project.cfg` does not exist' % code_path
            baw.utils.logging_error(msg)
            ret += 1
            continue
        cov_sources += '--cov=%s ' % code_path
    if ret:
        exit(ret)
    return cov_sources
