from os import makedirs
from os import scandir
from os.path import exists
from os.path import join
from shutil import rmtree
from sys import platform
from sys import stderr

from .utils import run

VIRTUAL_FOLDER = 'virtual'


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

    process = run(venv_command, virtual)
    if process.returncode == 0:
        return 0

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

    return run_virtual(install_requirements, path)


def run_virtual(root, command, cwd, env=None, *, verbose=False):
    """Run command with virtual environment

    Errors are printed to stdout.

    Args;
        command(str): command to execute
        cwd(str): working directoy where command is executed
        verbose(bool): if verbose, more logging is printed

    Returns:
        True if process is succesfull else False
    """
    virtual_path = join(root, 'virtual')
    activation_path = ('source', join(virtual_path, 'Scripts', 'activate'))
    if platform == 'win32':
        activation_path = join(virtual_path, 'Scripts', 'activate.bat')

    activate_and_execute = [
        activation_path,
        '&&',
        command,
    ]
    process = run(activate_and_execute, cwd, env=env)
    return process
