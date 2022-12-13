# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Python requirements parser
==========================

Example
-------

.. code-block:: txt

    # PyYAML==5.1
    # pdfminer.six==20181108

    # # Internal packages
    # iamraw==0.1.2
    # serializeraw==0.1.0
    # utila==0.5.3
"""

import contextlib
import dataclasses
import difflib
import re
import sys

import baw.project.version
import baw.utils


@dataclasses.dataclass
class Requirements:
    """\
    >>> str(Requirements(equal=dict(painter=('0.1.1', '0.1.1'))))
    'painter==0.1.1'
    >>> str(Requirements(equal=dict(rawmaker='1.0.0')))
    'rawmaker==1.0.0'
    """

    equal: dict = dataclasses.field(default_factory=dict)
    greater: dict = dataclasses.field(default_factory=dict)

    def __str__(self):
        result = [
            f'{package}=={version[0] if isinstance(version, tuple) else version}'
            for package, version in self.equal.items()
        ]
        greater = [
            f'{package}>={version}' if isinstance(version, str) else
            f'{package}>={version[0]}<{version[1]}'
            for package, version in self.greater.items()  # pylint:disable=E1101
        ]
        result.extend(greater)
        result = sorted(result, key=lambda x: x.lower())
        raw = '\n'.join(result)
        return raw


@dataclasses.dataclass
class NewRequirements(Requirements):

    def __getitem__(self, index):
        if not index:
            return self.equal
        if index == 1:
            return self.greater
        raise IndexError(f'{index} not supported')


def parse(content: str) -> Requirements:
    """\
    >>> parse('Flask_Login==0.1.1')
    Requirements(equal={'Flask_Login': '0.1.1'}, greater={})
    >>> parse('nltk==3.5')
    Requirements(equal={'nltk': '3.5.0'}, greater={})
    >>> parse('camelot_py[cv]>=0.8.2<0.9.0').greater
    {'camelot_py': ['0.8.2', '0.9.0']}
    """
    assert isinstance(content, str), content
    content = content.replace('-', '_')
    equal = {}
    greater = {}
    error = False
    for line in content.splitlines():
        try:
            if not (parsed := line_parse(line)):
                continue
        except ValueError:
            baw.utils.error(f'could not parse: "{line}"')
            error = True
        else:
            equal.update(parsed[0])
            greater.update(parsed[1])
    if error:
        return None
    common_keys = set(equal.keys()) | set(greater.keys())
    if len(common_keys) != (len(equal.keys()) + len(greater.keys())):
        baw.utils.error('duplicated package definition')
        baw.utils.error(content)
        sys.exit(baw.utils.FAILURE)
    result = Requirements(equal=equal, greater=greater)
    return result


def line_parse(line: str) -> tuple:
    """\
    >>> line_parse('nltk==3.5')
    ({'nltk': '3.5.0'}, {})
    >>> line_parse(' # be prosecuted under') is None
    True
    """
    line = line.strip()
    if not line or line.lstrip()[0] == '#':
        return None
    with contextlib.suppress(ValueError):
        # remove right side comment: 'rawmaker==1.0.0 # this is rawmaker'
        line = line.split('#')[0]
        # remove whitespace between comment and version sign
        line = line.strip()
    line = re.sub(r'\[\w{2,}\]', '', line)
    equal, greater = {}, {}
    if '==' in line:
        package, version = line.split('==')
        equal[package] = fix_version(version)
    elif '>=' in line:
        package, version = line.split('>=')
        version = fix_version(version)
        if '<' in version:
            version = version.split('<')
        if isinstance(version, str):
            greater[package] = fix_version(version)
        else:
            greater[package] = [fix_version(item) for item in version]
    else:
        # package without version
        equal[line] = ''
    return equal, greater


def fix_version(item: str, semver: bool = False) -> str:
    """\
    >>> fix_version('3.5')
    '3.5.0'
    >>> fix_version('20181108')
    '20181108'
    >>> fix_version('3.3.7.1', semver=True) # TODO: IMPROVE LATER
    '3.3.7'
    >>> fix_version('2.97.0.post5+7356925')
    '2.97.0.post5+7356925'
    >>> fix_version('2.97.0.post5+7356925', semver=True)
    '2.97.0+build5'
    """
    if '.' not in item:
        return item
    if semver and '.post' in item:
        item = item.split('+')[0]
        item = item.replace('.post', '+build')
        return item
    item = item.strip()
    if item.count('.') == 1:
        item = f'{item}.0'
    if semver:
        if item.count('.') == 3:
            item = item.rsplit('.', maxsplit=1)[0]
    return item


def diff(current: Requirements, requested: Requirements, minimal: bool = False):
    # TODO: SUPPORT GREATER THAN
    result = Requirements()
    for key, value in requested.equal.items():
        with contextlib.suppress(KeyError):
            if current.equal[key] == value:
                continue
        result.equal[key] = value  # pylint:disable=E1137
    for key, value in requested.greater.items():
        with contextlib.suppress(KeyError):
            if minimal:
                value = value[0], value[0]
            if inside(current.equal[key], value):
                continue
            if minimal:
                value = value[0]
        result.greater[key] = value  # pylint:disable=E1137
    return result


def replace(requirements: str, update: NewRequirements) -> str:
    for package, [old, new] in update.equal.items():
        # no version was given for old package
        pattern = f'{package}'
        if old:
            pattern += f'=={old}'
        replacement = f'{package}=={new}'
        baw.utils.log(f'replace requirement:\n{pattern}\n{replacement}')
        requirements = smart_replace(requirements, pattern, replacement)

    for package, [old, new] in update.greater.items():
        if isinstance(old, str):
            if lower(old, new):
                # skip lower version
                continue
            pattern = f'{package}>={old}'
            replacement = f'{package}>={new}'
        else:
            if lower(old[0], new):
                # skip lower version
                continue
            # TODO: first approach of greater equal replacement
            pattern = f'{package}>={old[0]}<{old[1]}'
            replacement = f'{package}>={new}<{old[1]}'

        if pattern == replacement:
            continue
        baw.utils.log(f'replace requirement:\n{pattern}\n{replacement}')
        requirements = smart_replace(requirements, pattern, replacement)
    return requirements


def smart_replace(requirements: str, old: str, new: str):
    """Ensure that `PyYAML==5.1.0` matches with `PyYAML==5.1` as `old`
    requirement line."""
    result = requirements
    result = [
        line
        if not difflib.get_close_matches(line, [old], n=1, cutoff=0.9) else new
        for line in result.splitlines()
    ]
    result = baw.utils.NEWLINE.join(result) + baw.utils.NEWLINE
    assert requirements != result, f'replacement does not work: {old}; {new}; {requirements}'
    return result


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
            if minor(current) >= minor(greater):  # pylint:disable=R5601,R5501
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
    """
    import semver
    current, new = fix_version(current, True), fix_version(new, True)
    try:
        current = semver.VersionInfo.parse(current)
    except ValueError:
        current: int = int(current)
    try:
        new = semver.VersionInfo.parse(new)
    except ValueError:
        new: int = int(new)
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
