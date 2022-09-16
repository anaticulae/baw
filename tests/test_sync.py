#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import pytest

import baw
import baw.cmd.sync
import baw.runtime
from baw.cmd.sync import sync


@pytest.mark.parametrize('venv', [False, True])
def test_sync(venv):
    if venv and not baw.runtime.has_virtual(baw.ROOT):
        pytest.skip('generate venv')
    sync(baw.ROOT, venv=venv, verbose=False)


def test_pip_list():
    parsed = baw.cmd.sync.pip_list(baw.ROOT, venv=False)
    assert len(parsed.equal) >= 10, parsed.equal
