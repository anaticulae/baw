#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import baw.cmd.sync
import baw.cmd.utils
import baw.run


def run(args: dict):
    root = baw.cmd.utils.run_environment(args)
    venv = args.get('venv', False)
    if venv:
        baw.run.run_venv(args)
    result = baw.cmd.sync.sync(
        root=root,
        packages=args.get('packages'),
        minimal=args.get('minimal', False),
        verbose=args.get('verbose', False),
        venv=venv,
    )
    return result


def extend_cli(parser):
    synx = parser.add_parser('rebase', help='Sync branches.')
    synx.add_argument(
        'branch',
        help='select branch',
        nargs='?',
        default='origin/master',
    )
    synx.set_defaults(func=run)
