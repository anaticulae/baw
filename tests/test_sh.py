# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import tests


@tests.longrun
def test_cmd_sh(simple, capsys):  # pylint:disable=W0621,W0613
    # stdout = tests.stdout(capsys)
    # assert 'README' in stdout
    # assert 'CHANGELOG' in stdout
    simple[0]('sh "ls"')


@tests.longrun
def test_cmd_sh_fail(simple, capsys):  # pylint:disable=W0621,W0613
    simple[0](
        'sh "invalid command"',
        expect=False,
    )
