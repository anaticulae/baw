# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import sys

# TODO: REMOVE LATER
import semantic_release.cli


def main():
    # run the patch
    import baw.changelog  # pylint:disable=W0611

    # rewrite argv
    sys.argv[0] = 'semantic_release'
    # invoke semantic release
    semantic_release.cli.entry()
