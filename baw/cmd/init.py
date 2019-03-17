###############################################################################
#                                Kiwi Project                                 #
#                                    2019                                     #
#                          Helmut Konrad Fahrendholz                          #
#                             kiwi@derspanier.de                              #
###############################################################################
from os import makedirs
from os.path import exists
from os.path import join
from subprocess import run

from ..config import create_config
from ..resources import FILES
from ..resources import FOLDERS
from ..utils import GIT_EXT


def init(root: str, shortcut: str, name: str):
    # create .baw, README etc
    for item in FOLDERS:
        create = join(root, item)
        if exists(create):
            continue
        makedirs(create)
        print('Create folder %s' % item)

    create_config(root, shortcut, name)

    for item, content in FILES:
        create = join(root, item)
        if exists(create):
            continue
        print('Create file %s' % item)
        with open(create, encoding='utf8', mode='a', newline='\n') as fp:
            fp.write(content)

    # git init
    git_dir = join(root, GIT_EXT)
    if exists(git_dir):
        return
    git_init = run(['git', 'init'])

    if git_init.returncode == 127:
        raise ChildProcessError('Git is not installed')
    if git_init.returncode:
        raise ChildProcessError('Could not run git init')

    # install pre-commits
