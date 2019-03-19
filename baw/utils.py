###############################################################################
#                                Kiwi Project                                 #
#                                    2019                                     #
#                          Helmut Konrad Fahrendholz                          #
#                             kiwi@derspanier.de                              #
###############################################################################

from configparser import ConfigParser
from contextlib import contextmanager
from os import environ
from subprocess import PIPE
from subprocess import run as run_sub
from sys import stderr

BAW_EXT = '.baw'
GIT_EXT = '.git'


@contextmanager
def handle_error(*exceptions, code=1):
    """Catch given `exceptions` and print there message to `stderr`. Exit
    system with given `code`.

    Args:
        exeception(iterable): of exception, which are handle by this context
        code(int): returned error-code
    Raises:
        SystemExitExecetion if given `exceptions` is raised while executing
        contextmanager.
    """
    try:
        yield
    except exceptions as error:
        print('[ERROR] %s' % error, file=stderr)
        exit(code)


def run(command, cwd, env=None):
    """Run external process and return an CompleatedProcess

    Args:
        command(str/iterable): command to execute
        cwd(str): working directory where the command is executed
    Returns:
        CompletedProcess with execution result
    """
    if not isinstance(command, str):
        command = ' '.join(command)

    process = run_sub(
        command,
        cwd=cwd,
        encoding='utf-8',
        env=env,
        shell=True,  # required for chaning commands
        stderr=PIPE,
        stdout=PIPE,
        universal_newlines=True,
    )
    return process


def flush():
    print('', end='', flush=True)


def get_setup():
    try:
        internal = int(environ['HELPY_INT_PORT'])
        external = int(environ['HELPY_EXT_PORT'])
        adress = environ['HELPY_URL']
        return (adress, internal, external)
    except KeyError as error:
        print_error('Missing global var %s' % error)
        exit(1)
