# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import subprocess

import baw.utils
from tests import example  # pylint:disable=W0611
from tests.fixtures.project import project_example  # pylint:disable=W0611
from tests.fixtures.project import project_example_done  # pylint:disable=W0611
from tests.fixtures.project import project_with_command  # pylint:disable=W0611
from tests.fixtures.project import project_with_test  # pylint:disable=W0611

pytest_plugins = 'pytester'  # pylint: disable=invalid-name

assert subprocess.run(
    ['which', 'baw'],
    capture_output=True,
    check=False,
).returncode == baw.utils.SUCCESS, 'require baw'
