#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""The test-startup starts with this file. If running on virtual environment,
installing baw is required. If baw-commands are skipped, cause of having very
fast feedback when only developing functions, baw will not installed.
"""
from sys import argv

from baw.runtime import VIRTUAL_FOLDER
from baw.runtime import run_target
from baw.utils import ROOT
from baw.utils import SUCCESS
from baw.utils import logging
from baw.utils import profile
from tests import FAST

pytest_plugins = 'pytester'  # pylint: disable=invalid-name


def install_baw():
    """Install baw-runtime to virtual environment"""
    logging('Install baw...')
    command = 'python setup.py install'
    completed = run_target(ROOT, command, ROOT, verbose=True)
    msg = 'Could not install required baw'

    assert completed.returncode == SUCCESS, msg

    completed = run_target(ROOT, 'baw --help', ROOT, verbose=False)
    assert completed.returncode == 0


RUN_VIRTUAL = VIRTUAL_FOLDER in ''.join(argv)
if RUN_VIRTUAL and not FAST:
    with profile():
        install_baw()
