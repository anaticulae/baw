###############################################################################
#                                Kiwi Project                                 #
#                                    2019                                     #
#                          Helmut Konrad Fahrendholz                          #
#                             kiwi@derspanier.de                              #
###############################################################################
"""Run every function which is used by `baw`."""

from contextlib import contextmanager
from contextlib import suppress
from functools import partial
from glob import glob
from os import environ
from os import remove
from os.path import abspath
from os.path import exists
from os.path import isfile
from os.path import join
from os.path import split
from os.path import splitdrive
from shutil import rmtree
from sys import stdout

from . import ROOT
from . import THIS
from .config import commands
from .config import minimal_coverage
from .config import shortcut
from .runtime import run_target
from .runtime import VIRTUAL_FOLDER
from .utils import BAW_EXT
from .utils import check_root
from .utils import get_setup
from .utils import GIT_EXT
from .utils import logging
from .utils import logging_error
from .utils import tmp


def root(cwd: str):
    """Determine root path of project.

    Iterate to the top directory while searching for GIT or BAW folder.

    Args:
        cwd(str): location where `baw` is executed
    Returns:
        path(str): of project-root(git)
    Raises:
        ValueError if no root is located or cwd does not exists
    """
    if not exists(cwd):
        raise ValueError('Current work directory does not exists %s' % cwd)

    cwd = abspath(cwd)  # ensure to work with absolut path
    if isfile(cwd):
        cwd = split(cwd)[0]  # remove filename out of path

    while True:
        if exists(join(cwd, GIT_EXT)):
            return cwd
        if exists(join(cwd, BAW_EXT)):
            return cwd
        cwd = abspath(join(cwd, '..'))
        if splitdrive(cwd)[1] == '\\':  #TODO: Windows only?
            msg = 'Could not determine project root. Current: %s' % cwd
            raise ValueError(msg)
    return cwd


def clean(root: str, virtual: bool = False):
    check_root(root)
    logging('Start cleaning')
    patterns = [
        '.coverage',
        '__pycache__',
        'build',
        'doctrees',
        'html',
        'tmp',
        VIRTUAL_FOLDER,
    ]

    # problems while deleting recursive
    for pattern in patterns:
        try:
            todo = glob(root + '/**/' + pattern, recursive=True)
        except NotADirectoryError:
            todo = glob(root + '**' + pattern, recursive=True)

        todo = sorted(todo, reverse=True)  # longtest path first, to avoid
        for item in todo:
            logging('Remove %s' % item)
            try:
                if isfile(item):
                    remove(item)
                else:
                    rmtree(item)
            except OSError as error:
                logging_error(error)
    logging()  # Newline


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


def test(root: str,
         *,
         coverage: bool = False,
         longrun: bool = False,
         pdb: bool = False,
         stash: bool = False,
         virtual: bool = False):
    """Running test-step in root/tests

    Args:
        longrun(bool): Runnig all tests
        pdf(bool): Run debugger on error
        stash(bool): Stash all changes to test commited-change in repository
        virtual(bool): run command in virtual environment
    Returns:
        returncode(int): 0 if successful else > 0
    """
    check_root(root)

    logging('Running tests')
    test_dir = join(root, 'tests')
    if not exists(test_dir):
        logging_error('No testdirectory %s available' % test_dir)
        exit(1)

    env = dict(environ.items())
    if longrun:
        env['LONGRUN'] = 'True'  # FAST = 'LONGRUN' not in environ.keys()

    debugger = '--pdb ' if pdb else ''
    cov = cov_args(root, pdb=debugger) if coverage else ''
    log_file = join(TMP(), 'tests.log')

    # using ROOT to get location from baw-tool
    test_config = join(ROOT, 'templates', 'pytest.ini')
    assert exists(test_config)

    cmd = ('pytest -c %s %s %s --log-file="%s" %s') % (
        test_config,
        debugger,
        cov,
        log_file,
        test_dir,
    )

    target = partial(
        run_target, root, cmd, cwd=test_dir, env=env, virtual=virtual)
    if stash:
        with git_stash(root, virtual):
            completed = target()
    else:
        completed = target()
    return completed.returncode


def cov_args(root: str, *, pdb: bool):
    """Determine args for running tests based on project-root

    Args:
        root(str): project root
        pdb(bool): using debugger on running tests

    Returns:
        args for coverage command
    """

    short = shortcut(root)
    source = join(root, short)
    tests = join(root, 'tests')
    output = join(TMP(), 'report')
    cov_config = join(ROOT, 'templates', '.coveragerc')
    assert exists(cov_config)

    #   --no-cov  Disable coverage report completely (useful for
    #             debuggers) default: False
    no_cov = '--no-cov ' if pdb else ''
    if no_cov:
        logging('Disable coverage report')

    min_cov = minimal_coverage(root)
    cov = ('--cov-config="%s" --cov="%s" --cov-report=html:%s --cov-branch'
           ' %s --cov-fail-under=%d') % (
               cov_config,
               source,
               output,
               no_cov,
               min_cov,
           )
    return cov


def doc(root: str, virtual: bool = False):
    """Run Sphinx doc generation

    The result is locatated in `doc/build` as html-report. The stderr and
    stdout are printed to console

    Exception:
        raises SystemExit if some error occurs"""
    doc = join(root, 'doc')
    doc_build = join(doc, 'build')
    # Create files out of source
    command = 'sphinx-apidoc -d 10 -M -f -e -o %s %s' % (doc_build, root)
    completed = run_target(root, command, virtual=virtual)

    if completed.returncode:
        return completed.returncode

    # Create html result
    logging('Running make html')

    build_options = [
        '-v ',
        # '-n',  # warn about all missing references
        # '-W',  # turn warning into error
        '-b coverage',
        '-j 8'
    ]
    build_options = ' '.join(build_options)

    command = 'sphinx-build -M html %s %s %s'
    command = command % (doc, doc, build_options)

    result = run_target(root, command, virtual=virtual)

    return result.returncode


def release(root: str, virtual: bool = False):
    ret = test(root, virtual=virtual, stash=True, longrun=True)
    if ret:
        logging_error('\nTests failed, could not release.\n')
        return ret

    logging("Update version tag")
    completed = run_target(root, 'semantic-release version')
    if completed.returncode:
        logging_error('while running semantic-release')
        return completed.returncode

    logging("Update Changelog")

    logging("Packing project")

    return 0


def head_tag(root: str, virtual: bool):
    command = 'git tag --points-at HEAD'

    completed = run_target(root, command, root, virtual=virtual)
    return completed.stdout.strip()


def publish(root: str, virtual: bool = False):
    tag = head_tag(root, virtual)
    if not tag:
        logging_error('Could not find release-git-tag. Aborting publishing.')
        return 1

    ret = release(root, virtual=virtual)
    if ret:
        exit(ret)

    adress, internal, _ = get_setup()
    url = '%s:%d' % (adress, internal)
    command = 'python setup.py sdist upload -r %s' % url
    completed = run_target(root, command, root, virtual=virtual)

    return completed.returncode


def sync(root: str, virtual: bool = False):
    check_root(root)
    logging('Sync dependencies')

    requirements_dev = 'requirements-dev.txt'
    resources = ['requirements.txt', requirements_dev]
    resources = [join(root, item) for item in resources]
    resources = [item for item in resources if exists(item)]

    if not exists(join(root, requirements_dev)):
        resources.append(abspath(join(THIS, '..', requirements_dev)))

    try:
        pip_index = environ['HELPY_INT_DIRECT']
        extra_url = environ['HELPY_EXT_DIRECT']
    except KeyError as error:
        logging_error('Global var %s does not exist' % error)
        exit(1)

    pip_source = '--index-url %s --extra-index-url %s' % (pip_index, extra_url)

    ret = 0
    for item in resources:
        cmd = 'python -mpip install %s -U -r %s' % (pip_source, item)
        logging(cmd)

        completed = run_target(root, cmd, cwd=root, virtual=virtual)

        if completed.stdout:
            logging(completed.stdout)
        if completed.returncode and completed.stderr:
            logging_error(completed.stderr)
        ret += completed.returncode
    return ret


SEPARATOR_WIDTH = 80


def run(root: str, virtual=False):
    """Check project-environment for custom run sequences, execute them from
    first to end.

    Args:
        root(str): project root where .baw and git are located
        virtual(bool): run in virtual environment
    Returns:
        0 if all sequences run succesfull else not 0
    """
    check_root(root)
    logging('Run')

    cmds = commands(root)
    if not cmds:
        logging_error('No commands available')
        return 1

    env = {} if virtual else dict(environ.items())
    ret = 0
    for command, executable in cmds.items():
        logging('\n' + command.upper().center(SEPARATOR_WIDTH, '*') + '\n')
        completed = run_target(root, executable, env=env, virtual=virtual)
        logging('\n' + command.upper().center(SEPARATOR_WIDTH, '='))

        ret += completed.returncode
    return ret
