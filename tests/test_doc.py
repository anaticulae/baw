# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import sys

import pytest

import tests


@pytest.mark.skipif(
    sys.hexversion >= 0x030900F0,
    reason='python 3.10, update Sphinx',
)
def test_cmd_doc(simple):
    # TODO: CHNAGE AFTER UPGRADING SPHINX
    simple[0]('doc')


@pytest.mark.skipif(
    sys.hexversion >= 0x030900F0,
    reason='python 3.10, update Sphinx',
)
@tests.nightly
def test_doc_cmd(project_example, monkeypatch):
    """Run doc cmd to generate documentation."""
    tests.baaw('doc', monkeypatch)
    created = project_example.join('tmpdir/docs/xcd/html/index.html')
    assert os.path.exists(created)
