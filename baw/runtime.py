###############################################################################
#                                Kiwi Project                                 #
#                                    2019                                     #
#                          Helmut Konrad Fahrendholz                          #
#                             kiwi@derspanier.de                              #
###############################################################################

from contextlib import contextmanager
from contextlib import suppress
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

from baw.utils import file_create
from baw.utils import file_read
from baw.utils import file_remove
from baw.utils import logging
from baw.utils import logging_error

VIRTUAL_FOLDER = 'virtual'

NO_EXECUTABLE = 127


def destroy(path: str):
    """Remove virtual path recursive if path exists, do nothing."""
    if not exists(path):
        logging('Nothing to clean, path does not exists %s' % path)
        return True
    logging('Removing virtual environment %s' % path)
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
        True if creating was successfull, else False and print stderr
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
        skip_error: set = None,
        verbose: bool = False,
        virtual: bool = False,
):
    if not cwd:
        cwd = root
    if not skip_error:
        skip_error = {}

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
            logging_error(error)
            return CompletedProcess(command, NO_EXECUTABLE)
    else:
        completed = _run_local(
            command,
            cwd=cwd,
            debugging=debugging,
            env=env,
        )

    reporting = verbose and completed.returncode not in skip_error
    if completed.returncode and reporting:
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
    virtual = join(root, VIRTUAL_FOLDER)

    activation = activation_path(root)
    deactivation = deactivation_path(root)
    if not exists(activation):
        msg = ('Path `%s` does not exists.\n'
               'Regenerate the virtual env') % activation
        raise RuntimeError(msg)

    execute = '%s && %s && %s' % (activation, command, deactivation)

    process = _run(execute, cwd, env, debugging=debugging)
    return process


def _run(command: str, cwd: str, env=None, debugging: bool = False):
    """

    Hint:
        Do not use stdout/stderr=PIPE, after this, running pdb with
        commandline is not feasible :) anymore. TODO: Investigate why.
    """
    if not env:
        env = dict(environ.items())

    # Capturering stdout and stderr reuqires PIPE in completed process.
    # Debugging with pdb due console require no PIPE.
    process = run(
        command,
        cwd=cwd,
        encoding='utf-8',
        env=env,
        shell=True,
        stderr=None if debugging else PIPE,
        stdout=None if debugging else PIPE,
        errors='xmlcharrefreplace',
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
    cmd = 'git stash --include-untracked'
    completed = run_target(root, cmd, virtual=virtual)
    with suppress(Exception):
        yield

    # unstash to recreate dirty environment
    cmd = 'git stash pop'
    completed = run_target(root, cmd, virtual=virtual)
