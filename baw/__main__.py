#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""Evaluate cmd-args and execute cmds"""

import sys
import traceback


def run():
    """Entry point of script"""
    try:
        import baw.dockers
        sys.exit(baw.dockers.switch_docker())
    except KeyboardInterrupt:
        import baw.utils
        baw.utils.log('\nOperation cancelled by user')
    except Exception as msg:  # pylint: disable=broad-except
        import baw.utils
        baw.utils.error(msg)
        stack_trace = traceback.format_exc()
        baw.utils.log(baw.utils.forward_slash(stack_trace))
    sys.exit(baw.FAILURE)


if __name__ == "__main__":
    run()
