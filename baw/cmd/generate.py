# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import baw.cmd.test
import baw.cmd.utils
import baw.utils


def run(args: dict):
    root = baw.cmd.utils.get_root(args)
    pattern = args.get('pattern')
    if pattern == 'all':
        return baw.cmd.test.run_test(
            root,
            generate=True,
            venv=args['venv'],
            verbose=args['verbose'],
        )
    return baw.utils.FAILURE


def extend_cli(parser):
    cli = parser.add_parser(
        'generate',
        help='Generate test data',
    )
    cli.add_argument(
        'pattern',
        help='Generate test data',
        nargs='?',
        const='all',
    )
    cli.add_argument(
        '--overwrite',
        help='overwrite already generated data',
        action='store_true',
    )
    cli.set_defaults(func=run)
