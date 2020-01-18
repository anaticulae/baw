# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import dataclasses
import enum
import os
import re

import baw.runtime
import baw.utils


class Status(enum.Enum):
    OPEN = enum.auto()
    INPROGESS = enum.auto()
    DONE = enum.auto()
    CLOSED = enum.auto()
    EMPTY = enum.auto()


@dataclasses.dataclass
class CodeQuality:
    coverage: float = None
    rating: float = None


def create():
    pass


def close():
    pass


def current(root: str) -> str:
    """Determine current open release plan name.

    Args:
        root: project root of analysed project
    Returns:
        current version number of newest release plan
        None if no release plan exists
    """
    # TODO: Validate versions
    listed = [item.replace('.rst', '') for item in os.listdir(releases(root))]
    versions = sorted([item for item in listed if '.' in item])
    if not versions:
        return None
    return versions[-1]


def releases(root: str) -> str:
    assert os.path.exists(root), root
    result = os.path.join(root, 'docs/releases')
    assert os.path.exists(result)
    return result


def current_plan(root: str) -> str:
    plan = current(root)
    if plan is None:
        return None
    source = releases(root)
    return os.path.join(source, f'{plan}.rst')


AFTER = """\
after
~~~~~

* Your code has been rated at
"""


def status(root: str) -> Status:
    plan = current_plan(root)
    if plan is None:
        return Status.EMPTY
    loaded = baw.utils.file_read(plan)
    todos = loaded.count('* [ ]')
    dones = loaded.count('* [x]')
    if todos:
        return Status.INPROGESS
    if not todos and dones:
        # decide closed ore done
        if AFTER in loaded:
            return Status.CLOSED
        return Status.DONE
    return Status.OPEN


def code_quality(root: str) -> CodeQuality:
    # Your code has been rated at 9.24/10
    completed = baw.runtime.run_target(
        root,
        command='baw --lint',
        skip_error_code=set(range(100)),
        verbose=False,
    )
    stdout = completed.stdout
    rating = re.search(
        r'Your code has been rated at (?P<major>\d{1,2})\.(?P<minor>\d{1,2})/10',
        stdout,
    )

    result = CodeQuality()
    if rating:
        result.rating = float(rating['major'] + '.' + rating['minor'])
    return result
