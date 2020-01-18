# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import pytest

import tests


@pytest.fixture
def project_example(testdir, monkeypatch):
    tests.run_command(['--init', 'xcd', '"I Like This Project"'], monkeypatch)
    tests.run_command(['--virtual'], monkeypatch)
    return str(testdir)
