#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
from os.path import join

from baw.cmd.upgrade import available_version
from baw.cmd.upgrade import determine_new_requirements
from baw.cmd.upgrade import installed_version
from baw.cmd.upgrade import parse_requirements
from baw.cmd.upgrade import replace_requirements
from baw.cmd.upgrade import upgrade_requirements
from baw.utils import file_create
from baw.utils import file_read
from baw.utils import ROOT

NEW_VERSION_AVAILABLE = """
utila (0.5.4)  - 0.5.4
  INSTALLED: 0.5.3
  LATEST:    0.5.4
"""

AVAILABLE_INSTALLED = """
utila (0.5.4)  - 0.5.4
  INSTALLED: 0.5.4 (latest)
"""

AVAILABLE_COMPLEX = """
pdfminer.six (20181108)  - 20181108
  INSTALLED: 20181108 (latest)
"""


def test_complex():
    available = available_version(AVAILABLE_COMPLEX)
    assert available == "20181108"

    installed = installed_version(AVAILABLE_COMPLEX)
    assert installed == "20181108"


def test_up_to_date():
    available = available_version(AVAILABLE_INSTALLED)
    assert available == "0.5.4"

    installed = installed_version(AVAILABLE_INSTALLED)
    assert installed == "0.5.4"


def test_out_of_date():
    available = available_version(NEW_VERSION_AVAILABLE)
    assert available == "0.5.4"

    installed = installed_version(NEW_VERSION_AVAILABLE)
    assert installed == "0.5.3"


REQUIREMENTS = """
PyYAML==5.1
pdfminer.six==20181108

# Internal packages
iamraw==0.1.2
serializeraw==0.1.0
utila==0.5.0

# without version
pip
"""

EXPECTED = {
    'PyYAML': '5.1',
    'iamraw': '0.1.2',
    'pdfminer.six': '20181108',
    'serializeraw': '0.1.0',
    'utila': '0.5.0',
    'pip': '',
}


def test_requirements_parser():
    result = parse_requirements(REQUIREMENTS)

    assert result == EXPECTED


def test_new_requirements():
    result = determine_new_requirements(ROOT, REQUIREMENTS)
    # utila should allways be new than 0.5.0
    assert 'utila' in result


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


def test_replace_requirements():
    upgrades = {
        'PyYAML': ('5.1', '6.3.2'),
        'utila': ('0.5.0', '3.5.0'),
    }

    replaced = replace_requirements(REQUIREMENTS, upgrades)

    assert replaced == REPLACED


TEST_UPGRADE = """\
utila==0.1.0
iamraw
"""


def test_upgrading(tmpdir):
    requirements_path = join(tmpdir, 'requirements.txt')

    file_create(requirements_path, TEST_UPGRADE)

    # use default requirements.txt
    upgrade_requirements(tmpdir, virtual=True)

    loaded = file_read(requirements_path)
    assert loaded != TEST_UPGRADE
