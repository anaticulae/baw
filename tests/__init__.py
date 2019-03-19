from os import environ
from os import makedirs
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import join
from random import randrange

import pytest

MAX_NUMBER = 20
MAX_TEST_RANDOM = 10**MAX_NUMBER

THIS = dirname(__file__)
PROJECT = abspath(join(THIS, '..'))
DATA = join(THIS, 'data')
# TEMP = join(PROJECT, 'build', 'temp')  # object not found
# makedirs(TEMP, exist_ok=True)

BAW_FOLDER = join(THIS,)
FAST = 'LONGRUN' not in environ.keys()
FAST_REASON = 'Takes to mutch time'

skip_longrunning = pytest.mark.skipif(
    FAST, reason="not implemented within werkzeug")


def tempname():
    """Get random file-name with 20-ziffre, random name

    Returns:
        filename(str): random file name
    """
    return str(randrange(MAX_TEST_RANDOM)).zfill(MAX_NUMBER)


def tempfile():
    """Get temporary file-path located in `TEMP_FOLDER`.

    Returns:
        filepath(str): to tempfile in TEMP_FOLDER
    """
    name = 'temp%s' % tempname()
    path = join(TEMP, name)
    if exists(path):
        return tempfile()
    return path
