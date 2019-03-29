###############################################################################
#                                Kiwi Project                                 #
#                                    2019                                     #
#                          Helmut Konrad Fahrendholz                          #
#                             kiwi@derspanier.de                              #
###############################################################################
from os import makedirs
from os.path import exists
from os.path import join
from shutil import copy
from subprocess import run

from baw import ROOT
from baw.config import create_config
from baw.config import name as project_name
from baw.config import shortcut
from baw.resources import FILES
from baw.resources import FOLDERS
from baw.resources import INIT
from baw.resources import TEMPLATES
from baw.runtime import NO_EXECUTABLE
from baw.utils import file_create
from baw.utils import GIT_EXT
from baw.utils import logging


def init(root: str, shortcut: str, name: str):
    create_folder(root)
    create_config(root, shortcut, name)
    add_init(root, shortcut)
    create_files(root)
    git_init(root)
    # install pre-commits


def add_init(root: str, shortcut: str):
    logging('Add __init__.py')
    init_dir = join(root, shortcut)
    makedirs(init_dir, exist_ok=True)
    file_create(join(init_dir, '__init__.py'), "__version__ = '0.0.0'\n")


def create_folder(root: str):
    # create .baw, README etc
    for item in FOLDERS:
        create = join(root, item)
        if exists(create):
            continue
        makedirs(create)
        print('Create folder %s' % item)

    create_config(root, shortcut, name)

def create_files(root: str):
    for item, content in FILES:
        create = join(root, item)
        replaced = replace_template(root, content)

        operation_type = 'template' if content != replaced else 'copy'
        if exists(create):
            skip('%s %s' % (operation_type, item))
            continue
        print('Create file %s' % item)
        with open(create, encoding='utf8', mode='a', newline='\n') as fp:
            fp.write(content)

        logging('%s %s' % (operation_type, item))
        file_create(create, content=replaced)


def replace_template(root: str, template: str):
    """Replace $vars in template

    Args:
        root(str): project root
        template(str): which contains the $_VARS_$
    Returns:
        content of template with replaced vars
    Hint:
        Vars are defined as $_VARNAME_$.
    """
    short = shortcut(root)
    name = project_name(root)

    template = template.replace('$_SHORT_$', short)
    template = template.replace('$_NAME_$', name)

    return template


def create_python(root: str):
    short = shortcut(root)

    python_project = join(root, short)
    makedirs(python_project, exist_ok=True)

    file_create(join(python_project, '__init__.py'), INIT)
    # file_create(join(python_project, '__init__.py'), INIT)


def evaluate_git_error(process):
    if process.returncode == NO_EXECUTABLE:
        raise ChildProcessError('Git is not installed')
    if process.returncode:
        raise ChildProcessError('Could not run git init')


def git_init(root: str):
    # git init
    git_dir = join(root, GIT_EXT)
    if exists(git_dir):
        skip('git init')
        return
    logging('git init')
    git_init = run(['git', 'init'])
    evaluate_git_error(git_init)


def git_add(root: str, pattern: str):
    logging('git add')
    add = run(['git', 'add', pattern])
    evaluate_git_error(add)


def skip(msg: str):
    logging('Skip: %s' % msg)
