# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from baw.resources import CODE_WORKSPACE
from baw.resources import RCFILE_PATH
from baw.resources import template_replace
from baw.utils import ROOT


def test_template_replace():
    """Test replace pattern from variable key word argument"""

    assert '{%RCFILE%}' in CODE_WORKSPACE
    assert RCFILE_PATH not in CODE_WORKSPACE

    replaced = template_replace(ROOT, CODE_WORKSPACE, rcfile=RCFILE_PATH)

    assert not '{%RCFILE%}' in replaced
    assert RCFILE_PATH in replaced
