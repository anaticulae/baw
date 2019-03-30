"""Evaluate cmd-args and execute commands"""

from os import getcwd
from os.path import dirname
from time import time

from baw import __version__
from baw.cmd import init as project_init
from baw.cmd import test
from baw.cmd.init import git_add
from baw.command import parse
from baw.execution import clean as project_clean
from baw.execution import doc
from baw.execution import publish
from baw.execution import release
from baw.execution import root as project_root
from baw.execution import run
from baw.execution import sync
from baw.runtime import create as create_virtual
from baw.utils import flush
from baw.utils import handle_error
from baw.utils import SUCCESS


def main():
    start = time()
    args = parse()
    if not any(args.values()):
        exit(SUCCESS)

    if args['version']:
        print(__version__)
        exit(SUCCESS)

    virtual = args['virtual']

    if args['init']:
        root = getcwd()
        with handle_error(ValueError):  #  TODO: Why?
            project_init(root, *args['init'])
            git_add(root, '*')
            release(root, virtual=virtual)

    with handle_error(ValueError):
        root = project_root(getcwd())

    if args['clean']:
        project_clean(root, virtual=virtual)

    ret = 0
    if virtual:
        ret += create_virtual(root)

    if args['sync']:
        ret += sync(root, virtual=virtual)

    if args['test']:
        ret += test(
            root,
            coverage='coverage' in args['test'],
            longrun='longrun' in args['test'],
            pdb='pdb' in args['test'],
            stash='stash' in args['test'],
            virtual=virtual)
    if args['doc']:
        ret += doc(root, virtual=virtual)

    if args['release']:
        ret += release(root, virtual=virtual)

    if args['publish']:
        ret += publish(root, virtual=virtual)

    if args['run']:
        ret += run(root, virtual=virtual)

    time_diff = time() - start
    print('Runtime: %.2f secs' % time_diff)
    exit(ret)


if __name__ == "__main__":
    main()
