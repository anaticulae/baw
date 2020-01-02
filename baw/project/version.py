#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
from os.path import exists
from os.path import join
from re import search

from baw.config import shortcut
from baw.utils import file_read


def version(root: str):
    """Determine current version out of __init__.py file

    Args:
        root(str): project root
    Returns:
        version number in format (x.y.z)
    Raises:
        ValueError if no __version__ can be located
    """
    assert exists(root)
    short = shortcut(root)

    path = join(root, '%s/__init__.py' % short)
    content = file_read(path)
    current = search(r'__version__ = \'(.*?)\'', content).group(1)
    if not current:
        raise ValueError('Could not locate __version__ in %s' % path)
    return current
