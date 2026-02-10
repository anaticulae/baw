# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import tests


def test_docker_flag(simple, capsys):  # pylint:disable=W0621,W0613
    simple[0]('pipe init')
    simple[0]('image create')
    simple[0]('--docker test -n1')


def test_docker_returncode(simple, capsys):  # pylint:disable=W0621,W0613
    simple[0]('pipe init')
    simple[0]('image create')
    simple[0]('--docker sh \'exit 1\'', expect=False)
    assert '[ERROR] Completed:' in tests.stdout(capsys)
