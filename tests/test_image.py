# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw.cmd.image
import tests


@tests.hasdocker
def test_cmd_image_create(simple, capsys):  # pylint:disable=W0621,W0613
    simple[0]('image create')


def test_image_create(simple, capsys):  # pylint:disable=W0621,W0613
    with baw.cmd.image.dockerfile(simple[1]) as path:
        assert os.path.exists(path)
