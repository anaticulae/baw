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

# support __version__ = "1.0.0" and __version__ = '1.0.0' and '1.0.0'
VERSION = (
    r'__version__ = [\'\"](.*?)[\'\"]',
    r'[\'\"](.*?)[\'\"]',
)


def determine(root: str) -> str:
    """Determine current version out of __init__.py file

    Args:
        root(str): project root
    Returns:
        version number in format (x.y.z)
    Raises:
        ValueError: if no __version__ can be located

    >>> import baw.project
    >>> determine(baw.project.determine_root(__file__))
    '...'
    """
    assert os.path.exists(root)
    # f'{short}/__init__.py:__version__'
    version_path = baw.config.version(root).rstrip(':__version__')
    path = os.path.join(root, version_path)
    content = baw.utils.file_read(path)
    for pattern in VERSION:
        parsed = re.search(pattern, content)
        if not parsed:
            continue
        current = parsed.group(1)
        break
    if not current:
        raise ValueError(f'Could not locate __version__ in {path}')
    return current


# TODO: IMPROVE THIS, USE EXTERNAL BIB
def major(item: str) -> int:
    """\
    >>> major('20220524')
    20220524
    """
    result = item.split('.')[0]
    result = int(result)
    return result


def minor(item: str) -> int:
    """\
    >>> minor('20220524')
    0
    """
    try:
        result = item.split('.')[1]
    except IndexError:
        return 0
    result = int(result)
    return result


def patch(item: str) -> int:
    """\
    >>> patch('2.1.3')
    3
    >>> patch('2.1')
    0
    >>> patch('20220524')
    0
    """
    try:
        result = item.split('.')[2]
    except IndexError:
        return 0
    result = int(result)
    return result
