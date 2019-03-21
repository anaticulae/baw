###############################################################################
#                                Kiwi Project                                 #
#                                    2019                                     #
#                          Helmut Konrad Fahrendholz                          #
#                             kiwi@derspanier.de                              #
###############################################################################

from os import environ
from os import makedirs
from os import scandir
from os.path import exists
from os.path import join
from shutil import rmtree
from subprocess import CompletedProcess
from subprocess import PIPE
from subprocess import run
from sys import platform
from sys import stderr

from .utils import logging
from .utils import logging_error

VIRTUAL_FOLDER = 'virtual'

NO_EXECUTABLE = 127


def destroy(path: str):
    """Remove virtual path recursive if path exists, do nothing."""
    if not exists(path):
        print('Nothing to clean, path does not exists %s' % path)
        return True
    print('Removing virtual environment %s' % path)
    rmtree(path)
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
    if clean and exists(virtual):
        destroy(virtual)

    if not exists(virtual):
        print('Creating virtual environment %s\n' % virtual, flush=True)
        makedirs(virtual)

    if exists(virtual) and list(scandir(virtual)):
        print('Using virtual environment %s\n' % virtual)
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
    process = _run(command=venv_command, cwd=virtual)
    if process.returncode == 0:
        return 0

    logging_error('While creating virutal environment')

    print(process.stdout, flush=True)
    print(process.stderr, file=stderr)
    return 1


def install_requirements(requirements: str, path: str):
    """Run pip with passed requirements file

    Args:
        requirement(str): path to requirements-file which is conform to pip -r
        path(str): location of virtual environment
    Returns:
        True if creating was successfull, else False and print stderr
    """

    install_requirements = 'python -mpip install -r %s' % requirements

    return run_target(path, install_requirements, virtual=True)


def run_target(root: str,
               command: str,
               cwd: str = None,
               env=None,
               virtual: bool = False):
    if not cwd:
        cwd = root

    if virtual:
        try:
            completed = _run_virtual(root, command, cwd=root, env=env)
        except RuntimeError as error:
            logging_error(error)
            return CompletedProcess(command, NO_EXECUTABLE)
    else:
        completed = _run_local(command, cwd=cwd, env=env)

    if completed.returncode:
        logging_error('Running `%(command)s` in `%(cwd)s` with:\n\n%(env)s' % {
            'command': command,
            'cwd': cwd,
            'env': env
        })

    if completed.stdout:
        logging(completed.stdout)

    if completed.stderr:
        logging_error(completed.stderr)

    return completed


def _run_local(command, cwd, env=None):
    """Run external process and return an CompleatedProcess

    Args:
        command(str/iterable): command to execute
        cwd(str): working directory where the command is executed
    Returns:
        CompletedProcess with execution result
    """
    if not isinstance(command, str):
        command = ' '.join(command)

    process = _run(command, cwd, env)

    return process


def _run_virtual(root, command, cwd, env=None):
    """Run command with virtual environment

    Args:
        root(str): project root to locate `virtual`-folder
        command(str): command to execute
        cwd(str): working directoy where command is executed

    Returns:
        CompletedProcess
    """
    virtual = join(root, VIRTUAL_FOLDER)
    activation_path = ('source', join(virtual, 'Scripts', 'activate'))
    if platform == 'win32':
        activation_path = join(virtual, 'Scripts', 'activate.bat')

    if not exists(activation_path):
        msg = ('Path `%s` does not exists. Regenerate the virtual env' %
               activation_path)
        raise RuntimeError(msg)

    activate_and_execute = [
        activation_path,
        '&&',
        command,
    ]
    activate_and_execute = ' '.join(activate_and_execute)

    process = _run(activate_and_execute, cwd, env)
    return process


def _run(command: str, cwd: str, env=None):
    """

    Hint:
        Do not use stdout/stderr=PIPE, after this, running pdb with
        commandline is not feasible :) anymore. TODO: Investigate why.
    """
    if not env:
        env = dict(environ.items())

    process = run(
        command,
        cwd=cwd,
        encoding='utf-8',
        env=env,
        shell=True,
        universal_newlines=True,
    )
    return process
