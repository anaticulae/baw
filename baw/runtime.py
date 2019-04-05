#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from contextlib import contextmanager
from os import environ
from os import makedirs
from os import scandir
from os.path import exists
from os.path import isdir
from os.path import join
from shutil import rmtree
from subprocess import CompletedProcess
from subprocess import PIPE
from subprocess import run
from sys import platform
from time import time

from baw.utils import FAILURE
from baw.utils import file_create
from baw.utils import file_read
from baw.utils import file_remove
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


def create(root: str, clean: bool = False):
    """Create `virtual` folder in project root, do nothing if folder exists

    This method creates the folder and does the init via python `venv`-module.

    Args:
        path(str): path for creating environment, if path already exists,
                   nothing happens
        clean(bool): virtual path is removed before creating new environment
    Returns:
        true if creating was succesfull, else False
    """
    virtual = join(root, VIRTUAL_FOLDER)

    if not exists(virtual):
        logging('Creating virtual environment %s\n' % virtual)
        makedirs(virtual)

    if exists(virtual) and list(scandir(virtual)):
        logging('Using virtual environment %s\n' % virtual)
        return 0

    venv_command = [
        "python",
        "-m",
        "venv",
        '.',
        '--copies',  # , '--system-site-packages'
    ]
    if clean:
        venv_command.append('--clear')
    venv_command = ' '.join(venv_command)
    process = _run(command=venv_command, cwd=virtual)
    if process.returncode == 0:
        __fix_environment(root)
        return 0

    logging_error('While creating virutal environment')

    logging(process.stdout)
    logging_error(process.stderr)

    return 1


def __fix_environment(root: str):
    path = activation_path(root)
    content = file_read(path)
    content = content.split(':END')[0]  # remove content after :END

    file_remove(path)
    file_create(path, content=content)


def install_requirements(requirements: str, path: str):
    """Run pip with passed requirements file

    Args:
        requirement(str): path to requirements-file which is conform to pip -r
        path(str): location of virtual environment
    Returns:
        True if creating was successful, else False and print stderr
    """

    install_requirements = 'python -mpip install -r %s' % requirements

    return run_target(path, install_requirements, virtual=True)


def run_target(
        root: str,
        command: str,
        cwd: str = None,
        env=None,
        *,
        debugging: bool = False,
        skip_error_code: set = None,
        skip_error_message: list = None,
        verbose: bool = True,
        virtual: bool = False,
):
    """Run target

    Args:
        root(str): project root of generated project
        command(str): command to run
        cwd(str): location where command is executed, if nothing is provided,
                  root is used.
        env(dict): environment variable, if nothing is passed, the global env
                   vars ared used

    Returns:
        CompletedProcess - os process which was runned
    """
    start = time()
    if not cwd:
        cwd = root

    if not exists(cwd):
        logging_error('cwd: %s does not exists' % cwd)
        return FAILURE

    if not isdir(cwd):
        logging_error('cwd: %s is not a directory' % cwd)
        return FAILURE

    if not skip_error_code:
        skip_error_code = {}

    if not skip_error_message:
        skip_error_message = []

    if virtual:
        try:
            completed = _run_virtual(
                root,
                command,
                cwd=root,
                debugging=debugging,
                env=env,
            )
        except RuntimeError as error:
            message = str(error)
            process = CompletedProcess(
                command,
                NO_EXECUTABLE,
                stdout=message,
                stderr=message,
            )
            return process
    else:
        completed = _run_local(
            command,
            cwd=cwd,
            debugging=debugging,
            env=env,
        )
    returncode = completed.returncode
    reporting = returncode and (returncode not in skip_error_code)
    if reporting:
        logging_error('Running `%(command)s` in `%(cwd)s`' % {
            'command': command,
            'cwd': cwd,
        })

    if completed.stdout and verbose:
        logging(completed.stdout)

    if verbose:
        if not reporting:
            # Inform, not writing to stderr
            logging('Running `%(command)s` in `%(cwd)s`\n' % {
                'command': command,
                'cwd': cwd,
            })
        logging('Env: %s' % environ)

    error_message = completed.stderr
    for remove_skip in skip_error_message:
        error_message = error_message.replace(remove_skip, '')

    if error_message.strip():
        logging_error(error_message)
    if verbose:
        print_runtime(start)

    return completed


def _run_local(command, cwd, env=None, debugging: bool = False):
    """Run external process and return an CompleatedProcess

    Args:
        command(str/iterable): command to execute
        cwd(str): working directory where the command is executed
    Returns:
        CompletedProcess with execution result
    """
    if not isinstance(command, str):
        command = ' '.join(command)
    process = _run(command, cwd, env, debugging=debugging)

    return process


def activation_path(root: str):
    virtual = join(root, VIRTUAL_FOLDER)
    path = join(virtual, 'Scripts', 'activate')
    if platform == 'win32':
        path = join(virtual, 'Scripts', 'activate.bat')
    return path


def deactivation_path(root: str):
    virtual = join(root, VIRTUAL_FOLDER)
    path = join(virtual, 'Scripts', 'deactivate')
    if platform == 'win32':
        path = join(virtual, 'Scripts', 'deactivate.bat')
    return path


def _run_virtual(root, command, cwd, env=None, debugging: bool = False):
    """Run command with virtual environment

    Args:
        root(str): project root to locate `virtual`-folder
        command(str): command to execute
        cwd(str): working directoy where command is executed

    Returns:
        CompletedProcess
    """
    activation = activation_path(root)
    deactivation = deactivation_path(root)
    if not exists(activation):
        msg = ('Path `%s` does not exists.\n'
               'Regenerate the virtual env') % activation
        raise RuntimeError(msg)

    execute = '%s && %s && %s' % (activation, command, deactivation)

    process = _run(execute, cwd, env=env, debugging=debugging)
    return process


def _run(command: str, cwd: str, env=None, debugging: bool = False):
    """

    Hint:
        Do not use stdout/stderr=PIPE, after this, running pdb with
        commandline is not feasible :) anymore. TODO: Investigate why.
    """
    if env is None:  # None: Empty dict is allowed.
        env = dict(environ.items())

    # Capturering stdout and stderr reuqires PIPE in completed process.
    # Debugging with pdb due console require no PIPE.
    process = run(
        command,
        cwd=cwd,
        encoding='utf8',
        env=env,
        shell=True,
        stderr=None if debugging else PIPE,
        stdout=None if debugging else PIPE,
        errors='ignore',
        universal_newlines=True,
    )
    return process


@contextmanager
def git_stash(root: str, virtual: bool):
    """Save uncommited/not versonied content to improve testability

    Args:
        root(str): root of execution
        virtual(bool): run in virtual environment

    """
    # TODO: Ivestigate here
    cmd = 'git stash --include-untracked'
    completed = run_target(root, cmd, virtual=virtual)

    error = None
    try:
        yield  # let user do there job
    except Exception as error:
        pass
    # unstash to recreate dirty environment
    cmd = 'git stash pop'
    completed = run_target(root, cmd, virtual=virtual)
    if completed.returncode:
        logging_error(completed.stderr)

    if error:
        raise error

    return completed.returncode
