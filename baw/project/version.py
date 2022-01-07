#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os
import re

import baw.config
import baw.utils

# support __version__ = "1.0.0" and __version__ = '1.0.0'
VERSION = r'__version__ = [\'\"](.*?)[\'\"]'


def determine(root: str) -> str:
    """Determine current version out of __init__.py file

    Args:
        root(str): project root
    Returns:
        version number in format (x.y.z)
    Raises:
        ValueError: if no __version__ can be located
    """
    assert os.path.exists(root)
    short = baw.config.shortcut(root)

    path = os.path.join(root, '%s/__init__.py' % short)
    content = baw.utils.file_read(path)
    current = re.search(VERSION, content).group(1)
    if not current:
        raise ValueError('Could not locate __version__ in %s' % path)
    return current


# TODO: IMPROVE THIS, USE EXTERNAL BIB
def major(item: str) -> int:
    result = item.split('.')[0]
    result = int(result)
    return result


def minor(item: str) -> int:
    result = item.split('.')[1]
    result = int(result)
    return result


def patch(item: str) -> int:
    result = item.split('.')[2]
    result = int(result)
    return result
