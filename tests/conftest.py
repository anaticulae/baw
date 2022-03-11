# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import subprocess

import baw.config
import baw.runtime
import baw.utils
from tests import example  # pylint:disable=W0611
from tests.fixtures.project import project_example  # pylint:disable=W0611

pytest_plugins = 'pytester'  # pylint: disable=invalid-name

if not 'PYTEST_XDIST_WORKER' in os.environ:
    # master process only
    if 'VIRTUAL' in os.environ:

        def run(cmd):
            result = subprocess.run(
                cmd,
                cwd=baw.ROOT,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
                timeout=5.0,
                check=False,
            )
            return result

        PYTHON = baw.config.python(baw.ROOT)
        # ensure that baw is installed
        COMPLETED = run(f'{PYTHON} setup.py install')
        assert COMPLETED.returncode == baw.utils.SUCCESS, COMPLETED

        COMPLETED = run('where baw')
        assert '.virtual' in COMPLETED.stdout.split()[0], COMPLETED
