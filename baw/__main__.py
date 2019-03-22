"""Evaluate cmd-args and execute commands"""

from os import getcwd
from os.path import dirname
from time import time

from . import __version__
from .cmd.init import init as project_init
from .command import parse
from .execution import clean as project_clean
from .execution import doc
from .execution import publish
from .execution import release
from .execution import root as project_root
from .execution import run
from .execution import sync
from .execution import test
from .runtime import create as create_virtual
from .utils import flush
from .utils import handle_error


def main():
    start = time()
    args = parse()
    if not any(args):
        exit(0)

    if args['version']:
        print(__version__)
        exit(0)

    if args['init']:
        with handle_error(ValueError):
            project_init(getcwd(), *args['init'])

    with handle_error(ValueError):
        root = project_root(getcwd())

    virtual = args['virtual']
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
            longrun='longrun' in args['test'],
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
