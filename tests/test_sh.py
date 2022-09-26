# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import tests


def test_cmd_sh(simple, capsys):  # pylint:disable=W0621
    simple[0]('sh ls')
    stdout = tests.stdout(capsys)
    assert 'README' in stdout
    assert 'CHANGELOG' in stdout
