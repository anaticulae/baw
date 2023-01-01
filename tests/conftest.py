# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import baw
from tests.fixtures.project import example  # pylint:disable=W0611
from tests.fixtures.project import project_example  # pylint:disable=W0611
from tests.fixtures.project import project_example_done  # pylint:disable=W0611
from tests.fixtures.project import project_with_cmd  # pylint:disable=W0611
from tests.fixtures.project import project_with_test  # pylint:disable=W0611
from tests.fixtures.project import simple  # pylint:disable=W0611

pytest_plugins = 'pytester'  # pylint: disable=invalid-name

assert baw.hasprog('baw'), 'install baw'
