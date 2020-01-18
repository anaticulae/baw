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

import baw.project.version
import baw.resources
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


def create(
        root: str,
        upgrade_major: bool = False,
        linter: float = 10.0,
        coverage: float = 100.0,
):
    major, minor = next_version(root, upgrade_major=upgrade_major)

    replaced = baw.resources.template_replace(
        root,
        template=baw.resources.RELEASE_PLAN,
        major=major,
        minor=minor,
        linter=linter,
        coverage=coverage,
    )
    outpath = os.path.join(releases(root), f'{major}.{minor}.0.rst')
    baw.utils.file_create(outpath, replaced)
    baw.utils.logging(f'create new release plan: {outpath}')

    # TODO: DIRY, REFACTOR
    message = f'releases(plan): add draft of release plan {major}.{minor}.0'
    baw.git.add(root, pattern=f'docs/releases/{major}.{minor}.0.rst')
    process = baw.runtime.run_target(root, f'git commit -m "{message}""')
    assert process.returncode == baw.utils.SUCCESS, process


def next_version(
        root: str,
        upgrade_major: bool = False,
):
    version = current(root)
    if version is None:
        version = '0.0.0'
    major, minor = (
        baw.project.version.major(version),
        baw.project.version.minor(version),
    )
    if upgrade_major:
        major = str(int(major) + 1)
    else:
        minor = str(int(minor) + 1)
    return major, minor


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

    # Total coverage: 0.00
    completed = baw.runtime.run_target(
        root,
        command='baw --test=cov --test=long --virtual',
        skip_error_code={1},
        verbose=False,
    )
    coverage = re.search(
        r'Total coverage: (?P<coverage>\d{1,3}\.\d{2})',
        completed.stdout,
    )
    if coverage:
        result.coverage = float(coverage['coverage'])
    return result
