# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from glob import glob
from os import chmod
from os import remove
from os.path import exists
from os.path import isfile
from os.path import join
from shutil import rmtree
from stat import S_IWRITE

from baw.runtime import VIRTUAL_FOLDER
from baw.utils import FAILURE
from baw.utils import SUCCESS
from baw.utils import check_root
from baw.utils import logging
from baw.utils import logging_error


def clean(root: str):
    check_root(root)
    logging('Start cleaning')
    patterns = [
        '*.egg',
        '*.egg-info',
        '*.swo',
        '*.swp',
        '.coverage',
        '.pytest_cache',
        '.tmp',
        '__pycache__',
        'build',
        'dist',
        'doctrees',
        'html',
        'nano.save',
    ]

    # problems while deleting recursive
    ret = 0
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
                    rmtree(item, onerror=remove_readonly)
            except OSError as error:
                ret += 1
                logging_error(error)
    if ret:
        exit(ret)
    logging()  # Newline
    return SUCCESS


def clean_virtual(root: str):
    """Clean virtual environment of given project

    Args:
        root(str): generated project
    Hint:
        Try to remove .virtual folder
    Raises:
        SystemExit if cleaning not work
    """
    virtual_path = join(root, VIRTUAL_FOLDER)
    if not exists(virtual_path):
        logging('Virtual environment does not exist %s' % virtual_path)
        return
    logging('Try to clean virtual environment %s' % virtual_path)
    try:
        rmtree(virtual_path)
    except OSError as error:
        logging_error(error)
        exit(FAILURE)
    logging('Finished')


def remove_readonly(func, path, _):
    "Clear the readonly bit and reattempt the removal"
    chmod(path, S_IWRITE)
    func(path)
