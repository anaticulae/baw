# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import tests


def test_run_doc(simple):
    simple[0]('doc')


@tests.nightly
def test_doc_cmd(project_example, monkeypatch):
    """Run doc cmd to generate documentation."""
    tests.baaw('sync all', monkeypatch)
    tests.baaw('doc', monkeypatch)
    created = project_example.join('tmpdir/docs/xcd/html/index.html')
    assert os.path.exists(created)
