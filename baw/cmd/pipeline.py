# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================


def extend_cli(parser):
    sync = parser.add_parser('pipeline', help='Run pipline task')
    sync.add_argument(
        'create',
        help='manage the jenkins file',
        nargs='?',
        const='test',
        choices='init upgrade test'.split(),
    )
