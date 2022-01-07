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
from baw.cmd.sync import sync


@pytest.mark.parametrize('virtual', [False, True])
def test_sync(virtual):
    sync(baw.ROOT, virtual=virtual, verbose=False)


def test_pip_list():
    parsed = baw.cmd.sync.pip_list(baw.ROOT, virtual=False)
    assert len(parsed.equal) >= 10, parsed.equal
