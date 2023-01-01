# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
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
