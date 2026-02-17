# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import re
import sys

import baw.requirements


def parse(content: str, upgrade: bool = False) -> baw.requirements.Requirements:
    r"""\
    >>> parse('Flask_Login==0.1.1')
    Requirements(equal={'Flask_Login': '0.1.1'}, greater={})
    >>> parse('nltk==3.5')
    Requirements(equal={'nltk': '3.5.0'}, greater={})
    >>> parse('camelot_py[cv]>=0.8.2<0.9.0').greater
    {'camelot_py': ['0.8.2', '0.9.0']}
    >>> parse('Flask_Login>=1.1.1\nFlask_Login==0.2.1')  # duplicated definition
    Traceback (most recent call last):
    ...
    SystemExit: 1
    """
    assert isinstance(content, str), content
    content = content.replace('-', '_')
    equal = {}
    greater = {}
    error = False
    for line in content.splitlines():
        try:
            if not (parsed := line_parse(line, upgrade=upgrade)):
                continue
        except ValueError:
            baw.error(f'could not parse: "{line}"')
            error = True
        else:
            equal.update(parsed[0])
            greater.update(parsed[1])
    if error:
        return None
    common_keys = set(equal.keys()) | set(greater.keys())
    if len(common_keys) != (len(equal.keys()) + len(greater.keys())):
        baw.error('duplicated package definition')
        baw.error(content)
        sys.exit(baw.FAILURE)
    result = baw.requirements.Requirements(equal=equal, greater=greater)
    return result


def line_parse(line: str, upgrade: bool = False) -> tuple:
    """\
    Use noauto to skip automated package upgrade. If upgrade is False,
    normal parser is used, cause we need it for sync resources etc.

    >>> line_parse('nltk==3.5')
    ({'nltk': '3.5.0'}, {})
    >>> line_parse(' # be prosecuted under') is None
    True
    >>> line_parse('iamraw>=3.5 # noauto', upgrade=True)
    skip: iamraw>=3.5 # noauto
    >>> line_parse('iamraw>=3.5 # noauto', upgrade=False)
    ({}, {'iamraw': '3.5.0'})
    >>> line_parse('docker >=7.1.0, <7.1.0')
    ({}, {'docker': ['7.1.0', '7.1.0']})
    """
    line = line.strip()
    if not line or line.lstrip()[0] == '#':
        return None
    if noauto := '#' in line and 'noauto' in line:  # pylint:disable=W0612
        if upgrade:
            baw.log(f'skip: {line}')
            return None
    with contextlib.suppress(ValueError):
        # remove right side comment: 'rawmaker==1.0.0 # this is rawmaker'
        line = line.split('#')[0]
        # remove whitespace between comment and version sign
        line = line.strip()
    line = line.replace(',', ' ')
    line = re.sub(r'\[\w{2,}\]', '', line)
    equal, greater = {}, {}
    if '==' in line:
        package, version = line.split('==')
        package, version = package.strip(), version.strip()
        equal[package] = fix_version(version)
    elif '>=' in line:
        package, version = line.split('>=')
        package, version = package.strip(), version.strip()
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
