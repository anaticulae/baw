from argparse import ArgumentParser
from collections import namedtuple

Command = namedtuple('Command', 'shortcut longcut message args')

all = Command('-a', '--all', 'Clean and run all exepect of publishing', None)
build = Command('-b', '--build', 'Run build tasks', None)
clean = Command('-c', '--clean', 'Delete build-, temp- and cache-folder', None)
doc = Command('-d', '--doc', 'Generate documentation with Sphinx', None)
init = Command('-i', '--init', 'Create .baw project', {
    'nargs': 2,
    'metavar': ('shorcut', 'name')
})
# run tests, increment version, commit, git tag
publish = Command('-p', '--publish', '', None)
docker = Command('-do', '--docker', 'Run commands in docker environment', None)
release = Command('-r', '--release', '', None)
report = Command('-re', '--report', 'Write module status in html report', None)
run = Command('-ru', '--run', 'Run application', None)
sync = Command('-s', '--sync', 'Sync dependencies', None)
test = Command('-t', '--test', 'Run tests and coverage', {
    'nargs': '?',
    'action': 'append',
    'choices': ['stash', 'longrun'],
})
venv = Command('-vi', '--virtual', 'Run commands in virtual environment', None)
version = ('-v', '--version', 'Show version of this program', None)


def create_parser():
    parser = ArgumentParser(prog='baw',)

    todo = (all, build, clean, doc, docker, init, publish, release, report, run,
            sync, test, venv, version)

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
    parser = create_parser()
    args = vars(parser.parse_args())
    need_help = not any(args.values())
    if need_help:
        parser.print_help()
        exit(1)
    return args
