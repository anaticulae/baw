# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import io
import sys

ENCODING = 'utf-8'


def main(remove_empty: bool = True):
    splitted = rawinput()
    splitted = set(splitted)
    splitted = sorted(splitted)
    valid = lambda x: True if not remove_empty else x.strip()
    unique = ''.join(item for item in splitted if valid(item))
    write_stdout(unique)


def rawinput(encoding=ENCODING) -> list:
    wrapper = io.TextIOWrapper(sys.stdin.buffer, encoding=encoding)
    result = wrapper.buffer.raw.readall().decode(encoding)
    result = result.splitlines(keepends=True)
    return result


def write_stdout(text, encoding=ENCODING):
    try:
        sys.stdout.flush()
        sys.stdout.buffer.write(text.encode(encoding))
        sys.stdout.buffer.flush()
    except BrokenPipeError:
        # for example | head does not want all the data we provide
        pass
