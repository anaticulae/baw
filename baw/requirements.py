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

import dataclasses

import baw.utils


@dataclasses.dataclass
class Requirements:
    equal: dict = dataclasses.field(default_factory=dict)
    greater: dict = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class NewRequirements(Requirements):

    def __getitem__(self, index):
        if index == 0:
            return self.equal
        if index == 1:
            return self.greater
        raise IndexError(f'{index} not supported')


def parse(content: str) -> Requirements:
    assert isinstance(content, str), content
    equal = {}
    greater = {}
    error = False
    for line in content.splitlines():
        line = line.strip()
        if not line or line[0] == '#':
            continue
        try:
            if '==' in line:
                package, version = line.split('==')
                equal[package] = version
            elif '>=' in line:
                package, version = line.split('>=')
                greater[package] = version
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
