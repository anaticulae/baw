#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import concurrent.futures
import os
import shutil
import subprocess
import sys
import time

import baw
import baw.config
import baw.utils

NO_EXECUTABLE = 127


def destroy(path: str):
    """Remove venv path recursive if path exists, do nothing."""
    if not os.path.exists(path):
        baw.log(f'Nothing to clean, path does not exists {path}')
        return True
    baw.log(f'Removing venv environment {path}')
    try:
        shutil.rmtree(path)
    except PermissionError as fail:
        # This error occurs, if an ide e.g. vscode uses the venv environment
        # so removing .venv folder is not possible.
        baw.error(fail)
        msg = f'Could not remove {path}. Path is locked by an other application.'
        baw.error(msg)
        return False
    return True


def run_target(
    root: str,
    cmd: str,
    cwd: str = None,
    env=None,
    *,
    debugging: bool = False,
    runtimelog: bool = True,
    skip_error_code: set = None,
    skip_error_message: list = None,
    verbose: int = 4,
) -> subprocess.CompletedProcess:
    """Run target

    Args:
        root(str): project root of generated project
        cmd(str): cmd to run
        cwd(str): location where cmd is executed, if nothing is provided,
                  root is used.
        env(dict): environment variable, if nothing is passed, the global env
                   vars ared used
        debugging(bool): run pdb if error occurs
        runtimelog(bool): print the duration of execution in secs
        skip_error_code(set): set of codes which are assumed that
                              process works successfully
        skip_error_message(list): list of error messages which are
                                  expected as no problem
        verbose(bool): explain what is beeing done

    Returns:
        CompletedProcess - os process which was runned
    """
    start = time.time()
    try:
        cwd, skip_error_code, skip_error_message = setup_target(
            root,
            cwd,
            skip_error_code,
            skip_error_message,
        )
    except ValueError as fail:
        baw.error(fail)
        return baw.FAILURE
    if verbose:
        baw.log(cmd)
    # run local
    completed = run(
        cmd=cmd,
        cwd=cwd,
        debugging=debugging,
        env=env,
    )
    log_result(
        completed,
        cwd,
        skip_error_code,
        skip_error_message,
        start if runtimelog else None,
        verbose,
    )
    return completed


def setup_target(
    root: str,
    cwd: str,
    skip_error_code,
    skip_error_message,
):
    if not cwd:
        cwd = root
    if not os.path.exists(cwd):
        raise ValueError(f'cwd: {cwd} does not exists')
    if not os.path.isdir(cwd):
        raise ValueError(f'cwd: {cwd} is not a directory')
    if not skip_error_code:
        skip_error_code = {}
    if isinstance(skip_error_code, int):
        skip_error_code: set = {skip_error_code}
    if not skip_error_message:
        skip_error_message = []
    return cwd, skip_error_code, skip_error_message


def log_result(  # pylint:disable=R1260,R0912
    completed: subprocess.CompletedProcess,
    cwd: str,
    skip_error_code: set,
    skip_error_message: list,
    start: int,
    verbose: int,
):
    """Log result to console.

    Args:
        completed(subprocess.CompletedProcess): finished process to log
        cwd(str): current work directory
        skip_error_code(set): set of error codes to handle not as error
        skip_error_message(list): list of error message to ignore
        start(int): unix time when process was started. If `start` is
                    None, no time exection log will be printed.
        verbose(int): state of verbosity. Verbose starts at the level 1.
    """
    cmd = completed.args
    returncode = completed.returncode
    if isinstance(skip_error_code, int):
        skip_error_code = {skip_error_code}
    reporting = returncode and (returncode not in skip_error_code)
    if reporting:
        msg = f'Completed: `{cmd}` in `{cwd}` returncode: {returncode}\n'
        baw.error(msg)
    if completed.stdout and verbose:
        baw.log(completed.stdout)
    if verbose:
        if not reporting:
            # Inform, not writing to stderr
            baw.log(f'Completed: `{cmd}` in `{cwd}`\n')
        if verbose == 2:  # TODO: Introduce VERBOSE level
            baw.log(f'Env: {os.environ}')
    error_message = completed.stderr
    # catch stderr is None when running baw --test=pdb because the std-out/err
    # is None
    if error_message is None:
        error_message = ''
    for remove_skip in skip_error_message:
        error_message = error_message.replace(remove_skip, '')
    if reporting and error_message.strip():
        baw.error(error_message.strip())
    if verbose:
        baw.completed(completed)
        if start is not None:
            baw.utils.print_runtime(start)


def run(
    cmd: str,
    cwd: str = None,
    env=None,
    debugging: bool = False,
    live: bool = False,
):
    """Run process.

    Hint:
        Do not use stdout/stderr=PIPE, after this, running pdb with
        cmdline is not feasible :) anymore. TODO: Investigate why.
    """
    if not isinstance(cmd, str):
        cmd = ' '.join(cmd)
    if env is None:  # None: Empty dict is allowed.
        env = dict(os.environ.items())
    if live:
        debugging = True
    # Capturering stdout and stderr reuqires PIPE in completed process.
    # Debugging with pdb due console requires no PIPE.
    process = subprocess.run(  # pylint:disable=W1510 # nosec
        cmd,
        cwd=cwd,
        encoding=baw.utils.UTF8,
        env=env,
        shell=True,
        stderr=None if debugging else subprocess.PIPE,
        stdout=None if debugging else subprocess.PIPE,
        errors='ignore',
        universal_newlines=True,
        check=False,
    )
    return process


def runs(
    cmds: str,
    cwd: str,
    verbose: int = 0,
    workers: int = 12,
) -> int:
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        waitfor = []
        for cmd in cmds:
            waitfor.append(executor.submit(
                run,
                cmd=cmd,
                cwd=cwd,
            ))
        for future in concurrent.futures.as_completed(waitfor):
            completed = future.result()
            if completed.returncode:
                baw.error(f'error: {completed.stderr}')
                return baw.FAILURE
    if verbose:
        baw.log(f'{cmds}: complete\n')
    return baw.SUCCESS


def installed(program: str, root: str):
    done = run_target(
        root,
        cmd=f'which {program}',
        verbose=False,
    )
    if done.returncode == baw.SUCCESS:
        return True
    baw.error(f'not installed: {program}')
    baw.error(f'python: {sys.executable}')
    baw.error(f'path: {" ".join(sys.path)}')
    return False


def hasprog(program: str):
    assert program, 'define program'
    completed = subprocess.run(  # pylint:disable=c2001 # nosec
        f'which {program}'.split(),
        check=False,
        capture_output=True,
    )
    isinstalled = completed.returncode == baw.SUCCESS
    if isinstalled:
        expected = f'{program}:'
        if completed.stdout.strip() in (expected, expected.encode('utf8')):
            # workaround for `whereis` of arch
            isinstalled = False
    return isinstalled


def iswin():
    return 'win' in sys.platform
