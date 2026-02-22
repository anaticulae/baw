# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import semver

import baw.project.version
import baw.requirements.parser


def lower(current: str, new: str) -> bool:
    """Verify if the `new` requirement is older than the `current`.

    >>> lower('1.26.2', '1.26.1')
    True
    >>> lower('1.5', '20.2.3')
    False
    >>> lower('3.3.7.1', '4.0.0') # TODO: INVESTIGATE LATER
    False
    >>> lower('2.97.0.post5+7356925', '2.97.0')
    True
    >>> lower('2.97.0.post5+abcde', '2.97.0.post5+abcde')
    False
    >>> lower('2.97.0.post5+abcde', '2.97.0.post4+bcde')
    True
    >>> lower('20221105', '20221105')
    False
    """
    current = baw.requirements.parser.fix_version(current, True)
    new: str = baw.requirements.parser.fix_version(new, True)
    try:
        current: semver.Version = semver.Version.parse(current)
    except ValueError:
        current: int = int(current)
    try:
        new: semver.Version = semver.Version.parse(new)
    except ValueError:
        new: int = int(new)
    if isinstance(new, int):
        return new < current
    if new == current:
        if current.build and new.build:
            curr = current.build.split('+')[0][4:]
            neww = new.build.split('+')[0][4:]
            return neww < curr
        if current.build:
            # post5+7356925
            return True
        if new.build:
            # post5+7356925
            return False
    return new < current


def inside(current: str, expected: str) -> bool:  # pylint:disable=R1260,R0911,R0912
    """\
    >>> inside('2.12.0', '2.14.0<3.0.0')
    False
    >>> inside('2.17.0', '2.14.0<2.16.0')
    False
    >>> inside('2.16.0', '2.14.0<2.16.0')
    False
    >>> inside('2.16.0', '2.14.0<=2.16.0')
    True
    >>> inside('0.1.2', ['0.1.3', '1.0.0'])
    False
    >>> inside('0.1.4', ['0.1.3', '1.0.0'])
    True
    >>> inside('0.2.6', ['0.2.6', '0.2.6'])
    True
    >>> inside('20220524', '20220524')
    True
    >>> inside('2.97.0', ['2.97.0.post5+7356925', '3.0.0'])
    False
    """
    if not isinstance(expected, str):
        if expected[0] != expected[1]:
            expected = '<'.join(expected)
        else:
            expected = '<='.join(expected)
    if '<' in expected:
        split = expected.split('<=') if '<=' in expected else expected.split(
            '<')
        small, greater = split
    elif expected.isdigit():
        return current == expected
    else:
        small, greater = expected, expected
    major = baw.project.version.major
    minor = baw.project.version.minor
    patch = baw.project.version.patch
    if not major(small) <= major(current) <= major(greater):
        return False
    if major(small) == major(current):
        if minor(current) < minor(small):
            return False
    if major(greater) == major(current):
        if '<=' in expected:
            if minor(current) > minor(greater):
                return False
        else:
            if minor(current) >= minor(greater):  # pylint:disable=R5501
                return False
    if major(small) == major(current) and minor(small) == minor(current):
        if patch(small) > patch(current):
            return False
        if pre(current) < pre(small):
            # ('2.97.0', ['2.97.0.post5+7356925', '3.0.0'])
            return False
    return True


def pre(item: str) -> int:
    """\
    >>> pre('2.97.0.post5+7356925')
    5
    """
    if '.post' not in item:
        return 0
    item = item.split('.post')[1]
    item = item.split('+')[0]
    item = int(item)
    return item
