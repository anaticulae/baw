# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import sys


def main():
    import semantic_release.cli

    # run the patch
    import baw.changelog  # pylint:disable=W0611

    # rewrite argv
    sys.argv[0] = 'semantic_release'
    # invoke semantic release
    semantic_release.cli.entry()
