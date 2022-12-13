# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import baw.cmd.upgrade
import baw.requirements
import baw.requirements.parser
import baw.requirements.upgrade
import tests.fixtures.requirements

REPLACED = """
PyYAML==6.3.2
pdfminer.six==20181108

# Internal packages
iamraw==0.1.2
serializeraw==0.1.0
utila==3.5.0

# without version
pip
"""

REQUIREMENTS_GREATER = """
PyYAML==5.1
pdfminer.six>=20181108
utila>=0.5.0
"""

EXPECTED = {
    'PyYAML': '5.1.0',
    'iamraw': '0.1.2',
    'pdfminer.six': '20181108',
    'serializeraw': '0.1.0',
    'utila': '0.5.0',
    'pip': '',
}

EXPECTED_GREATER = {
    'pdfminer.six': '20181108',
    'utila': '0.5.0',
}


def test_replace_requirements():
    upgrades = baw.requirements.NewRequirements(
        equal={
            'PyYAML': ('5.1', '6.3.2'),
            'utila': ('0.5.0', '3.5.0'),
        },
        greater={},
    )
    replaced = baw.requirements.upgrade.replace(
        tests.fixtures.requirements.REQUIREMENTS,
        upgrades,
    )
    assert replaced == REPLACED


def test_requirements_parser():
    result = baw.requirements.parser.parse(
        tests.fixtures.requirements.REQUIREMENTS)
    assert result, 'requirements parsing error'
    assert result.equal == EXPECTED


def test_requirements_parser_greater_equal():
    result = baw.requirements.parser.parse(REQUIREMENTS_GREATER)
    assert result, 'requirements parsing error'
    assert result.greater == EXPECTED_GREATER


def test_requirements_diff_equal():
    parsed = baw.requirements.parser.parse(
        tests.fixtures.requirements.REQUIREMENTS)
    empty = baw.requirements.upgrade.diff(parsed, parsed)
    assert not empty.equal, empty


def test_requirements_diff():
    current = baw.requirements.Requirements(equal={
        'PyYAML': '5.1',
    })
    requested = baw.requirements.Requirements(equal={
        'PyYAML': '5.1',
        'pdfminer.six': '20181108',
    })
    expected = baw.requirements.Requirements(equal={
        'pdfminer.six': '20181108',
    })
    diff = baw.requirements.upgrade.diff(current, requested)
    assert diff == expected
