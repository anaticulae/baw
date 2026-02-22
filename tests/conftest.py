# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import pytest

import baw
from tests.fixtures.project import example  # pylint:disable=W0611
from tests.fixtures.project import project_example  # pylint:disable=W0611
from tests.fixtures.project import project_example_done  # pylint:disable=W0611
from tests.fixtures.project import project_with_cmd  # pylint:disable=W0611
from tests.fixtures.project import project_with_test  # pylint:disable=W0611
from tests.fixtures.project import simple  # pylint:disable=W0611

pytest_plugins = 'pytester'  # pylint: disable=invalid-name

assert baw.hasprog('baw'), 'install baw'
assert baw.hasprog('git'), 'install git'


@pytest.fixture(scope="session", autouse=True)
def git_identity_for_tests():
    os.environ["GIT_AUTHOR_NAME"] = "Super Mario"
    os.environ["GIT_AUTHOR_EMAIL"] = "test@example.com"
    os.environ["GIT_COMMITTER_NAME"] = "Super Mario"
    os.environ["GIT_COMMITTER_EMAIL"] = "test@example.com"
