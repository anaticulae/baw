# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import time

# pylint:disable=C0209


def today() -> str:
    """Determine date in `german` format"""
    cur = time.localtime(time.time())
    return "%02d.%02d.%04d" % (cur.tm_mday, cur.tm_mon, cur.tm_year)


def current(seconds: bool = False, separator: str = ':') -> str:
    """Determine time in `german` format"""
    cur = time.localtime(time.time())
    if seconds:
        return "%02d%s%02d%s%02d" % (cur.tm_hour, separator, cur.tm_min,
                                     separator, cur.tm_sec)
    return "%02d%s%02d" % (cur.tm_hour, separator, cur.tm_min)


def timedate():
    return '%s %s' % (current(), today())
