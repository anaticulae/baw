# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================


def select_cov(args):
    """Select optional cov path or default one, or no cov.

    --cov
    >>> select_cov(dict(cov=None))
    True

    --cov=/var/workdir
    >>> select_cov(dict(cov='/var/workdir'))
    '/var/workdir'

    >>> select_cov(dict(cov='NOT_SELECTED'))
    False
    """
    if args['cov'] == 'NOT_SELECTED':
        return False
    if args['cov']:
        # --cov=/var/workdir
        return args['cov']
    # --cov without data
    return True
