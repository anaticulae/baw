#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
import pytest

from baw.cmd.sync import sync
from baw.utils import ROOT


@pytest.mark.parametrize('virtual', [False, True])
def test_sync(virtual):
    sync(ROOT, virtual=virtual, verbose=False)
