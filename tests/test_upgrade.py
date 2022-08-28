#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
import os
import textwrap

import baw.cmd.upgrade
import baw.requirements
import baw.runtime
import tests
import tests.fixtures.project
import tests.fixtures.requirements

# fixture
project_example = tests.fixtures.project.project_example  # pylint:disable=C0103

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

AVAILABLE_MULTIPLE = """
utilatest (0.1.5)  - 0.1.5
  INSTALLED: 0.1.4
  LATEST:    0.1.5
utila (2.11.0)     - 2.11.0
"""


def test_complex():
    available = baw.cmd.upgrade.available_version(AVAILABLE_COMPLEX)
    assert available == "20181108"

    installed = baw.cmd.upgrade.installed_version(AVAILABLE_COMPLEX)
    assert installed == "20181108"


def test_available_multiple():
    available = baw.cmd.upgrade.available_version(
        AVAILABLE_MULTIPLE,
        package='utila',
    )
    assert available == "2.11.0"


MULTIPLE = """
data_sections (0.1.0)  - 0.1.0
sections (1.18.0)      - 1.18.0
  INSTALLED: 1.18.0 (latest)
"""


def test_available_multiple_second():
    available = baw.cmd.upgrade.available_version(
        MULTIPLE,
        package='sections',
    )
    assert available == '1.18.0'


def test_up_to_date():
    available = baw.cmd.upgrade.available_version(AVAILABLE_INSTALLED)
    assert available == "0.5.4"

    installed = baw.cmd.upgrade.installed_version(AVAILABLE_INSTALLED)
    assert installed == "0.5.4"


def test_out_of_date():
    available = baw.cmd.upgrade.available_version(NEW_VERSION_AVAILABLE)
    assert available == "0.5.4"

    installed = baw.cmd.upgrade.installed_version(NEW_VERSION_AVAILABLE)
    assert installed == "0.5.3"


@tests.longrun
def test_new_requirements():
    result = baw.cmd.upgrade.determine_new_requirements(
        baw.ROOT,
        tests.fixtures.requirements.REQUIREMENTS,
    )
    # utila should allways be new than 0.5.0
    assert 'utila' in result[0]


TEST_UPGRADE = """\
utila==0.1.0
iamraw
"""


def test_upgrading(tmpdir):
    requirements_path = os.path.join(tmpdir, baw.utils.REQUIREMENTS_TXT)

    baw.utils.file_create(requirements_path, TEST_UPGRADE)

    # use default requirements.txt
    baw.cmd.upgrade.upgrade_requirements(tmpdir)

    loaded = baw.utils.file_read(requirements_path)
    assert loaded != TEST_UPGRADE


@tests.hasgit
@tests.longrun
@tests.nonvirtual
def test_upgrade_requirements(project_example, capsys):  # pylint: disable=W0621, W0613
    path = os.getcwd()

    def commit_all():
        completed = baw.runtime.run_target(
            path,
            'git add . && git commit -m "Upgade requirements"',
        )
        assert completed.returncode == baw.utils.SUCCESS, str(completed)

    # yapf in a higher version is provided by dev environment
    baw.utils.file_append(baw.utils.REQUIREMENTS_TXT, 'yapf==0.10.0')

    failed_test = textwrap.dedent("""\
    def test_me():
        assert 0
    """)
    failingtest_path = 'tests/test_failed.py'

    baw.utils.file_create(failingtest_path, failed_test)
    commit_all()

    result = baw.cmd.upgrade.upgrade(
        path,
        verbose=True,
        virtual=True,
        generate=False,  # do not change - see test.py/generate_only
    )
    assert result == baw.utils.FAILURE
    stdout = capsys.readouterr().out

    assert stdout
    assert 'Reset' in stdout, stdout

    # Reuse virtual environment
    # remove failling test
    baw.utils.file_remove(failingtest_path)
    commit_all()

    result = baw.cmd.upgrade.upgrade(
        path,
        verbose=False,
        virtual=True,
        generate=False,  # see above
    )
    assert result == baw.utils.SUCCESS
