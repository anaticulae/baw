#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import subprocess
from os import environ
from os import makedirs
from os import scandir
from os.path import exists
from os.path import isdir
from os.path import join
from shutil import rmtree
from sys import platform
from time import time

from baw.utils import FAILURE
from baw.utils import SUCCESS
from baw.utils import UTF8
from baw.utils import file_create
from baw.utils import file_read
from baw.utils import file_remove
from baw.utils import file_replace
from baw.utils import logging
from baw.utils import logging_error
from baw.utils import print_runtime

VIRTUAL_FOLDER = '.virtual'

NO_EXECUTABLE = 127


def destroy(path: str):
    """Remove virtual path recursive if path exists, do nothing."""
    if not exists(path):
        logging('Nothing to clean, path does not exists %s' % path)
        return True
    logging('Removing virtual environment %s' % path)
    try:
        rmtree(path)
    except PermissionError as error:
        # This error occurs, if an ide e.g. vscode uses the virtual environment
        # so removing .virtual folder is not possible.
        msg = 'Could not remove %s. Path is locked by an other application.'
        logging_error(error)
        logging_error(msg % path)
        return False
    return True


def venv(root: str) -> str:
    assert root
    return join(root, VIRTUAL_FOLDER)


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
    virtual = join(root, VIRTUAL_FOLDER)

    if not exists(virtual):
        logging(f'create virtual: {virtual}')
        makedirs(virtual)

    if exists(virtual) and list(scandir(virtual)):
        logging(f'virtual: {virtual}')
        return SUCCESS

    venv_command = [
        "python",
        "-m",
        "venv",
        '.',
        '--copies',  # , '--system-site-packages'
    ]
    if clean:
        venv_command.append('--clear')
    cmd = ' '.join(venv_command)  # TODO: Is this required?
    process = _run(command=cmd, cwd=virtual)

    patch_pip(root)

    if process.returncode:
        logging_error('While creating virutal environment')

        logging(process.stdout)
        logging_error(process.stderr)

        return FAILURE

    if verbose:
        logging(process.stdout)
        if process.stderr:
            logging_error(process.stderr)
    return SUCCESS


def patch_pip(root):
    """This patch is required for install pdfminer.six==20181108 under
    pip==18.1, this can may be removed with new pip or pdfminer. There is a
    problem with sorting RECORS, cause mixing sort int and str.

    TODO: REMOVE WITH UPGRADED PIP OR PDFMINER
    """
    logging('Patching the wheel')

    to_patch = join(root, '.virtual/Lib/site-packages/pip/_internal/wheel.py')
    if not exists(to_patch):
        return
    template = 'for row in sorted(outrows):'
    replacement = 'for row in outrows:'
    content = file_read(to_patch).replace(template, replacement)
    file_replace(to_patch, content)


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
        debugging(bool): run pdf if error occurs
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
    except ValueError as error:
        logging_error(str(error))
        return FAILURE

    if virtual:
        try:
            completed = _run_virtual(
                root,
                cmd=command,
                cwd=root,
                debugging=debugging,
                env=env,
            )
        except RuntimeError as error:
            message = str(error)
            process = subprocess.CompletedProcess(
                command,
                NO_EXECUTABLE,
                stdout=message,
                stderr=message,
            )
            return process
    else:
        # run local
        completed = _run(
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
    if not skip_error_message:
        skip_error_message = []
    return cwd, skip_error_code, skip_error_message


def log_result(  # pylint:disable=R1260
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
    reporting = returncode and (returncode not in skip_error_code)
    if reporting:
        msg = f'Completed: `{command}` in `{cwd}` returncode: {returncode}\n'
        logging_error(msg)

    if completed.stdout and verbose:
        logging(completed.stdout)

    if verbose:
        if not reporting:
            # Inform, not writing to stderr
            logging(f'Completed: `{command}` in `{cwd}`\n')
        if verbose == 2:  # TODO: Introduce VERBOSE level
            logging('Env: %s' % environ)

    error_message = completed.stderr
    # catch stderr is None when running baw --test=pdb because the std-out/err
    # is None
    if error_message is None:
        error_message = ''
    for remove_skip in skip_error_message:
        error_message = error_message.replace(remove_skip, '')

    if reporting and error_message.strip():
        logging_error('%s' % error_message.strip())
    if verbose:
        if completed.stderr:
            logging_error(completed.stderr)
        if completed.stdout:
            logging(completed.stdout)
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
        cwd(str): working directoy where command is executed
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

    start = 'sh' if platform == 'win32' else 'source'
    end = '' if platform == 'win32' else 'source'
    execute = f'{start} {activate} && {cmd} && {end} {deactivate}'
    process = _run(execute, cwd, env=env, debugging=debugging)

    return process


def _run(command: str, cwd: str, env=None, debugging: bool = False):
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
    process = subprocess.run(
        command,
        cwd=cwd,
        encoding=UTF8,
        env=env,
        shell=True,
        stderr=None if debugging else subprocess.PIPE,
        stdout=None if debugging else subprocess.PIPE,
        errors='ignore',
        universal_newlines=True,
    )
    return process
