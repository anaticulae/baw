# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import argparse
import os
import pstats

import baw.utils


def main():
    parser = create_parser()
    args = parser.parse_args()
    for path in files(args):
        profile_show(path)
    return baw.SUCCESS


def files(args):
    result = []
    for path in args.files:
        if not os.path.exists(path):
            baw.error(f'file does not exists: {path}')
            continue
        abspath = os.path.abspath(path)
        result.append(abspath)
    return result


def profile_show(path: str):
    result = pstats.Stats(path)
    result.sort_stats('tottime')
    # limit number of calls
    # TODO: REMOVE THIS HACK
    result.fcn_list = result.fcn_list[0:500]
    result.print_stats()


def create_parser():
    parser = argparse.ArgumentParser(prog='baw_cprofile_show')
    parser.add_argument(
        'files',
        help='files to evaluate',
        nargs='+',
    )
    # TODO: ADD ARG TO SHOW AS HTML
    return parser
