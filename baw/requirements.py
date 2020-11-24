# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
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

import baw.project.version
import baw.utils


@dataclasses.dataclass
class Requirements:
    equal: dict = dataclasses.field(default_factory=dict)
    greater: dict = dataclasses.field(default_factory=dict)

    def __str__(self):
        result = [
            f'{package}=={version}' for package, version in self.equal.items()  # pylint:disable=E1101
        ]
        result = sorted(result)
        raw = '\n'.join(result)
        return raw


@dataclasses.dataclass
class NewRequirements(Requirements):

    def __getitem__(self, index):
        if index == 0:
            return self.equal
        if index == 1:
            return self.greater
        raise IndexError(f'{index} not supported')


def parse(content: str) -> Requirements:
    """\
    >>> parse('Flask_Login==0.1.1')
    Requirements(equal={'Flask_Login': '0.1.1'}, greater={})
    """
    assert isinstance(content, str), content
    equal = {}
    greater = {}
    error = False
    for line in content.splitlines():
        line = line.strip()
        if not line or line[0] == '#':
            continue
        with contextlib.suppress(ValueError):
            # remove right side comment: 'rawmaker==1.0.0 # this is rawmaker'
            line = line.split('#')[0]
            # remove whitespace between comment and version sign
            line = line.strip()
        try:
            if '==' in line:
                package, version = line.split('==')
                equal[package] = version.strip()
            elif '>=' in line:
                package, version = line.split('>=')
                greater[package] = version.strip()
            else:
                # package without version
                equal[line] = ''
        except ValueError:
            baw.utils.logging_error(f'could not parse: "{line}"')
            error = True
    if error:
        return None

    common_keys = set(equal.keys()) | set(greater.keys())
    if len(common_keys) != (len(equal.keys()) + len(greater.keys())):
        baw.utils.logging_error('duplicated package definition')
        baw.utils.logging_error(content)
        exit(baw.utils.FAILURE)

    result = Requirements(equal=equal, greater=greater)
    return result


def diff(current: Requirements, requested: Requirements):
    # TODO: SUPPORT GREATER THAN
    result = Requirements()
    for key, value in requested.equal.items():
        with contextlib.suppress(KeyError):
            if current.equal[key] == value:
                continue
        result.equal[key] = value  # pylint:disable=E1137
    return result


def replace(requirements: str, update: NewRequirements) -> str:
    for package, [old, new] in update.equal.items():
        if old:
            pattern = f'{package}=={old}'
        else:
            # no version was given for old package
            pattern = f'{package}'
        replacement = f'{package}=={new}'

        baw.utils.logging(f'replace requirement:\n{pattern}\n{replacement}')
        requirements = requirements.replace(pattern, replacement)

    for package, [old, new] in update.greater.items():
        pattern = f'{package}>={old}'
        replacement = f'{package}>={new}'

        baw.utils.logging(f'replace requirement:\n{pattern}\n{replacement}')
        requirements = requirements.replace(pattern, replacement)
    return requirements


def inside(current: str, expected: str) -> bool:
    """\
    >>> inside('2.12.0', '2.14.0<3.0.0')
    False
    >>> inside('2.17.0', '2.14.0<2.16.0')
    False
    >>> inside('2.16.0', '2.14.0<2.16.0')
    False
    >>> inside('2.16.0', '2.14.0<=2.16.0')
    True
    """
    split = expected.split('<=') if '<=' in expected else expected.split('<')
    small, greater = split
    major = baw.project.version.major
    minor = baw.project.version.minor

    if not (major(small) <= major(current) <= major(greater)):
        return False

    if major(small) == major(current):
        if minor(current) < minor(small):
            return False

    if major(greater) == major(current):
        if '<=' in expected:
            if minor(current) > minor(greater):
                return False
        else:
            if minor(current) >= minor(greater):
                return False

    return True
