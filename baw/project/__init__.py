#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from os import environ
from os.path import abspath
from os.path import exists
from os.path import isfile
from os.path import join
from os.path import split
from os.path import splitdrive

from baw.git import GIT_EXT
from baw.utils import BAW_EXT


def find_root(cwd: str):
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
