###############################################################################
#                                Kiwi Project                                 #
#                                    2019                                     #
#                          Helmut Konrad Fahrendholz                          #
#                             kiwi@derspanier.de                              #
###############################################################################
"""Define structure of command line interface."""

from argparse import ArgumentParser
from collections import namedtuple

Command = namedtuple('Command', 'shortcut longcut message args')

ALL = Command('-a', '--all', 'Clean and run all exepect of publishing', None)
BUILD = Command('-b', '--build', 'Run build tasks', None)
CLEAN = Command('-c', '--clean', 'Delete build-, temp- and cache-folder', None)
DOC = Command('-d', '--doc', 'Generate documentation with Sphinx', None)
INIT = Command('-i', '--init', 'Create .baw project', {
    'nargs': 2,
    'metavar': ('shortcut', 'name'),
})
# run tests, increment version, commit, git tag and push to package index
PUSH = Command('-p', '--publish', 'Push release to repository', None)
DOCKER = Command('-do', '--docker', 'Run commands in docker environment', None)
RELEASE = Command(
    '-r',
    '--release',
    'Test and tag current commit as new release',
    None,
)
REPORT = Command('-re', '--report', 'Write module status in html report', None)
RUN = Command('-ru', '--run', 'Run application', None)
SYNC = Command('-s', '--sync', 'Sync dependencies', None)
TEST = Command(
    '-t', '--test', 'Run tests and coverage', {
        'nargs': '?',
        'action': 'append',
        'choices': ['coverage', 'pdb', 'stash', 'longrun'],
    })
VENV = Command('-vi', '--virtual', 'Run commands in virtual environment', None)
VERSION = ('-v', '--version', 'Show version of this program', None)


def create_parser():  # noqa: Z21
    """Create parser out of defined dictonary with command-line-definiton.

    Returns created argparser
    """
    parser = ArgumentParser(prog='baw')
    todo = (
        ALL,
        BUILD,
        CLEAN,
        DOC,
        DOCKER,
        INIT,
        PUSH,
        RELEASE,
        REPORT,
        RUN,
        SYNC,
        TEST,
        VENV,
        VERSION,
    )

    for shortcut, longcut, msg, args in todo:
        shortcuts = (shortcut, longcut)
        add = parser.add_argument
        if args:
            args['help'] = msg
            add(*shortcuts, **args)
        else:
            add(*shortcuts, action='store_true', help=msg)
    return parser


def parse():
    """Parse arguments from sys-args and return the result as dictonary."""
    parser = create_parser()
    args = vars(parser.parse_args())
    need_help = not any(args.values())
    if need_help:
        parser.print_help()
    return args
