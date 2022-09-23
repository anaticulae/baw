#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os
import shutil
import subprocess
import sys
import time

import baw.config
import baw.utils

VENV_FOLDER = '.venv'

NO_EXECUTABLE = 127


def destroy(path: str):
    """Remove venv path recursive if path exists, do nothing."""
    if not os.path.exists(path):
        baw.utils.log(f'Nothing to clean, path does not exists {path}')
        return True
    baw.utils.log(f'Removing venv environment {path}')
    try:
        shutil.rmtree(path)
    except PermissionError as fail:
        # This error occurs, if an ide e.g. vscode uses the venv environment
        # so removing .venv folder is not possible.
        baw.utils.error(fail)
        msg = f'Could not remove {path}. Path is locked by an other application.'
        baw.utils.error(msg)
        return False
    return True


def virtual(root: str, creates: bool = True) -> str:
    assert root
    name: str = 'global'
    if not baw.config.venv_global():
        name = baw.config.shortcut(root)
    venv = os.path.join(baw.config.bawtmp(), 'venv', name)
    if os.path.exists(venv):
        return venv
    outdated = os.path.join(root, VENV_FOLDER)
    if os.path.exists(outdated):
        baw.utils.error(f'use outdated venv: {outdated}')
        return outdated
    if creates:
        os.makedirs(venv, exist_ok=True)
    return venv


def has_virtual(root: str) -> bool:
    assert root
    venv = virtual(root, creates=False)
    if os.path.exists(venv):
        return True
    return False


def create(root: str, clean: bool = False, verbose: bool = False) -> int:
    """Create `venv` folder in project root, do nothing if folder exists

    This method creates the folder and does the init via python `venv`-module.

    Args:
        root(str): project root
        clean(bool): venv path is removed before creating new environment
        verbose(bool): explain what is being done
    Returns:
        SUCCESS if creating was was succesfull else FAILURE
    """
    venv = virtual(root)
    if not os.path.exists(venv):
        baw.utils.log(f'create venv: {venv}')
        os.makedirs(venv, exist_ok=True)
    if os.path.exists(venv) and list(os.scandir(venv)):
        baw.utils.log(f'venv: {venv}')
        return baw.utils.SUCCESS
    python = baw.config.python(root, venv=False)
    # '--system-site-packages'
    cmd = f'{python} -m virtualenv . --copies '
    if clean:
        cmd = f'{cmd} --clear'
    process = run(command=cmd, cwd=venv)
    patch_pip(root)
    if sys.version_info.major == 3 and sys.version_info.minor == 7:
        # python 3.7
        patch_env(root)
    if process.returncode:
        baw.utils.error(cmd)
        baw.utils.error('While creating virutal environment:')
        baw.utils.log(process.stdout)
        baw.utils.error(process.stderr)
        return baw.utils.FAILURE
    if verbose:
        baw.utils.log(process.stdout)
        if process.stderr:
            baw.utils.error(process.stderr)
    return baw.utils.SUCCESS


def patch_pip(root):
    """This patch is required for install pdfminer.six==20181108 under
    pip==18.1, this can may be removed with new pip or pdfminer. There is a
    problem with sorting RECORS, cause mixing sort int and str.

    TODO: REMOVE WITH UPGRADED PIP OR PDFMINER
    """
    baw.utils.log(f'Patching the wheel: {root}')
    to_patch = os.path.join(
        virtual(root),
        'Lib/site-packages/pip/_internal/wheel.py',
    )
    if not os.path.exists(to_patch):
        return
    template = 'for row in sorted(outrows):'
    replacement = 'for row in outrows:'
    content = baw.utils.file_read(to_patch).replace(template, replacement)
    baw.utils.file_replace(to_patch, content)


def patch_env(root):
    path = os.path.join(virtual(root), 'Scripts/activate.bat')
    content = baw.utils.file_read(path)
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
    venv: bool = False,
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
        venv(bool): run in venv environment

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
        baw.utils.error(str(fail))
        return baw.utils.FAILURE
    if verbose:
        baw.utils.log(command)
    if venv:
        try:
            completed = _run_venv(
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
    if not os.path.exists(cwd):
        raise ValueError('cwd: %s does not exists' % cwd)
    if not os.path.isdir(cwd):
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
        baw.utils.error(msg)
    if completed.stdout and verbose:
        baw.utils.log(completed.stdout)
    if verbose:
        if not reporting:
            # Inform, not writing to stderr
            baw.utils.log(f'Completed: `{command}` in `{cwd}`\n')
        if verbose == 2:  # TODO: Introduce VERBOSE level
            baw.utils.log('Env: %s' % os.environ)
    error_message = completed.stderr
    # catch stderr is None when running baw --test=pdb because the std-out/err
    # is None
    if error_message is None:
        error_message = ''
    for remove_skip in skip_error_message:
        error_message = error_message.replace(remove_skip, '')
    if reporting and error_message.strip():
        baw.utils.error('%s' % error_message.strip())
    if verbose:
        if completed.stderr:
            baw.utils.error(completed.stderr)
        if completed.stdout:
            baw.utils.log(completed.stdout)
        if start is not None:
            baw.utils.print_runtime(start)


def _run_venv(
    root: str,
    cmd: str,
    cwd: str,
    env: dict = None,
    debugging: bool = False,
) -> subprocess.CompletedProcess:
    """Run command with venv environment

    Args:
        root(str): project root to locate `venv`-folder
        cmd(str): command to execute
        cwd(str): working directory where command is executed
        env(dict): replace enviroment variables
        debugging(bool): run pdb when error occurs
    Raises:
        RuntimeError: if venv path does not exists
    Returns:
        CompletedProcess
    """
    iswin = sys.platform == 'win32'
    activate = os.path.join(
        virtual(root),
        'Scripts' if iswin else 'bin',
        'activate',
    )
    deactivate = os.path.join(virtual(root), 'Scripts/deactivate')
    if not os.path.exists(activate):
        msg = (f'Path `{activate}` does not exists.\nRegenerate the venv')
        raise RuntimeError(msg)
    if iswin:
        activate = f'{activate}.bat'
        deactivate = f'{deactivate}.bat'
    else:
        activate = f'source {activate}'
        # linux does not require a deactivate script, its just a function
        # which was create by activate
        deactivate = 'deactivate'
    execute = f'{activate} && {cmd} && {deactivate}'
    process = run(
        execute,
        cwd,
        env=env,
        debugging=debugging,
    )
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
        env = dict(os.environ.items())
    # Capturering stdout and stderr reuqires PIPE in completed process.
    # Debugging with pdb due console requires no PIPE.
    process = subprocess.run(  # pylint:disable=W1510 # nosec
        command,
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


def installed(program: str, root: str, venv: bool = False):
    done = run_target(
        root,
        command=f'which {program}',
        venv=venv,
        verbose=False,
    )
    if done.returncode == baw.utils.SUCCESS:
        return True
    baw.utils.error(f'not installed: {program}')
    baw.utils.error(f'venv: {venv}')
    baw.utils.error(f'python: {sys.executable}')
    baw.utils.error(f'path: {" ".join(sys.path)}')
    return False


def hasprog(program: str):
    assert program, 'define program'
    completed = subprocess.run(  # pylint:disable=c2001 # nosec
        f'which {program}'.split(),
        check=False,
        capture_output=True,
    )
    isinstalled = completed.returncode == baw.utils.SUCCESS
    if isinstalled:
        expected = f'{program}:'
        if completed.stdout.strip() in (expected, expected.encode('utf8')):
            # workaround for `whereis` of arch
            isinstalled = False
    return isinstalled
