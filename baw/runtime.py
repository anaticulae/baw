#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os
import subprocess
import sys
from os import environ
from os import makedirs
from os import scandir
from os.path import exists
from os.path import isdir
from os.path import join
from shutil import rmtree
from sys import platform
from time import time

import baw.config
import baw.utils
from baw.utils import FAILURE
from baw.utils import SUCCESS
from baw.utils import UTF8
from baw.utils import error
from baw.utils import file_read
from baw.utils import file_replace
from baw.utils import log
from baw.utils import print_runtime

VIRTUAL_FOLDER = '.virtual'

NO_EXECUTABLE = 127


def destroy(path: str):
    """Remove virtual path recursive if path exists, do nothing."""
    if not exists(path):
        log('Nothing to clean, path does not exists %s' % path)
        return True
    log('Removing virtual environment %s' % path)
    try:
        rmtree(path)
    except PermissionError as fail:
        # This error occurs, if an ide e.g. vscode uses the virtual environment
        # so removing .virtual folder is not possible.
        msg = 'Could not remove %s. Path is locked by an other application.'
        error(fail)
        error(msg % path)
        return False
    return True


def venv(root: str) -> str:
    assert root
    name = baw.config.shortcut(root)
    virtual = os.path.join(baw.config.bawtmp(), 'venv', name)
    if os.path.exists(virtual):
        return virtual
    outdated = join(root, VIRTUAL_FOLDER)
    if os.path.exists(outdated):
        baw.utils.error(f'use outdated virtual: {outdated}')
        return outdated
    os.makedirs(virtual, exist_ok=True)
    return virtual


def create(root: str, clean: bool = False, verbose: bool = False) -> int:
    """Create `virtual` folder in project root, do nothing if folder exists

    This method creates the folder and does the init via python `venv`-module.

    Args:
        root(str): project root
        clean(bool): virtual path is removed before creating new environment
        verbose(bool): explain what is being done
    Returns:
        SUCCESS if creating was was succesfull else FAILURE
    """
    virtual = venv(root)

    if not exists(virtual):
        log(f'create virtual: {virtual}')
        makedirs(virtual, exist_ok=True)

    if exists(virtual) and list(scandir(virtual)):
        log(f'virtual: {virtual}')
        return SUCCESS

    python = baw.config.python(root, virtual=False)
    venv_command = [
        python,
        "-m",
        "virtualenv",
        '.',
        '--copies',  # , '--system-site-packages'
    ]
    if clean:
        venv_command.append('--clear')
    cmd = ' '.join(venv_command)  # TODO: Is this required?
    process = run(command=cmd, cwd=virtual)

    patch_pip(root)
    if sys.version_info.major == 3 and sys.version_info.minor == 7:
        # python 3.7
        patch_env(root)

    if process.returncode:
        error(' '.join(venv_command))
        error('While creating virutal environment:')

        log(process.stdout)
        error(process.stderr)

        return FAILURE

    if verbose:
        log(process.stdout)
        if process.stderr:
            error(process.stderr)
    return SUCCESS


def patch_pip(root):
    """This patch is required for install pdfminer.six==20181108 under
    pip==18.1, this can may be removed with new pip or pdfminer. There is a
    problem with sorting RECORS, cause mixing sort int and str.

    TODO: REMOVE WITH UPGRADED PIP OR PDFMINER
    """
    log('Patching the wheel')

    to_patch = join(root, '.virtual/Lib/site-packages/pip/_internal/wheel.py')
    if not exists(to_patch):
        return
    template = 'for row in sorted(outrows):'
    replacement = 'for row in outrows:'
    content = file_read(to_patch).replace(template, replacement)
    file_replace(to_patch, content)


def patch_env(root):
    path = join(root, '.virtual/Scripts/activate.bat')
    content = file_read(path)
    content = content.split(':END')[0]  # remove content after :END

    baw.utils.file_remove(path)
    baw.utils.file_create(path, content=content)


def run_target(
    root: str,
    command: str,
    cwd: str = None,
    env=None,
    *,
    debugging: bool = False,
    runtimelog: bool = True,
    skip_error_code: set = None,
    skip_error_message: list = None,
    verbose: bool = True,
    virtual: bool = False,
) -> subprocess.CompletedProcess:
    """Run target

    Args:
        root(str): project root of generated project
        command(str): command to run
        cwd(str): location where command is executed, if nothing is provided,
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
        virtual(bool): run in virtual environment

    Returns:
        CompletedProcess - os process which was runned
    """
    start = time()

    try:
        cwd, skip_error_code, skip_error_message = setup_target(
            root,
            cwd,
            skip_error_code,
            skip_error_message,
        )
    except ValueError as fail:
        error(str(fail))
        return FAILURE

    if verbose:
        log(command)

    if virtual:
        try:
            completed = _run_virtual(
                root,
                cmd=command,
                cwd=root,
                debugging=debugging,
                env=env,
            )
        except RuntimeError as fail:
            message = str(fail)
            process = subprocess.CompletedProcess(
                command,
                NO_EXECUTABLE,
                stdout=message,
                stderr=message,
            )
            return process
    else:
        # run local
        completed = run(
            command=command,
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
    if not exists(cwd):
        raise ValueError('cwd: %s does not exists' % cwd)
    if not isdir(cwd):
        raise ValueError('cwd: %s is not a directory' % cwd)
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
    command = completed.args
    returncode = completed.returncode
    if isinstance(skip_error_code, int):
        skip_error_code = {skip_error_code}
    reporting = returncode and (returncode not in skip_error_code)
    if reporting:
        msg = f'Completed: `{command}` in `{cwd}` returncode: {returncode}\n'
        error(msg)

    if completed.stdout and verbose:
        log(completed.stdout)

    if verbose:
        if not reporting:
            # Inform, not writing to stderr
            log(f'Completed: `{command}` in `{cwd}`\n')
        if verbose == 2:  # TODO: Introduce VERBOSE level
            log('Env: %s' % environ)

    error_message = completed.stderr
    # catch stderr is None when running baw --test=pdb because the std-out/err
    # is None
    if error_message is None:
        error_message = ''
    for remove_skip in skip_error_message:
        error_message = error_message.replace(remove_skip, '')

    if reporting and error_message.strip():
        error('%s' % error_message.strip())
    if verbose:
        if completed.stderr:
            error(completed.stderr)
        if completed.stdout:
            log(completed.stdout)
        if start is not None:
            print_runtime(start)


def _run_virtual(
    root: str,
    cmd: str,
    cwd: str,
    env: dict = None,
    debugging: bool = False,
) -> subprocess.CompletedProcess:
    """Run command with virtual environment

    Args:
        root(str): project root to locate `virtual`-folder
        cmd(str): command to execute
        cwd(str): working directory where command is executed
        env(dict): replace enviroment variables
        debugging(bool): run pdb when error occurs
    Raises:
        RuntimeError: if virtual path does not exists
    Returns:
        CompletedProcess
    """
    activate = join(root, VIRTUAL_FOLDER, 'Scripts', 'activate')
    deactivate = join(root, VIRTUAL_FOLDER, 'Scripts', 'deactivate')
    if not exists(activate):
        msg = (f'Path `{activate}` does not exists.\n'
               'Regenerate the virtual env')
        raise RuntimeError(msg)

    if platform == 'win32':
        activate = f'{activate}.bat'
        deactivate = f'{deactivate}.bat'
    else:
        activate = f'source {activate}'
        deactivate = f'source {deactivate}'

    execute = f'{activate} && {cmd} && {deactivate}'
    process = run(execute, cwd, env=env, debugging=debugging)

    return process


def run(command: str, cwd: str, env=None, debugging: bool = False):
    """Run process.

    Hint:
        Do not use stdout/stderr=PIPE, after this, running pdb with
        commandline is not feasible :) anymore. TODO: Investigate why.
    """
    if not isinstance(command, str):
        command = ' '.join(command)
    if env is None:  # None: Empty dict is allowed.
        env = dict(environ.items())
    # Capturering stdout and stderr reuqires PIPE in completed process.
    # Debugging with pdb due console requires no PIPE.
    process = subprocess.run(  # pylint:disable=W1510
        command,
        cwd=cwd,
        encoding=UTF8,
        env=env,
        shell=True,
        stderr=None if debugging else subprocess.PIPE,
        stdout=None if debugging else subprocess.PIPE,
        errors='ignore',
        universal_newlines=True,
        check=False,
    )
    return process
