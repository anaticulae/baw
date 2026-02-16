#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os

import baw.cmd.upgrade
import baw.requirements.upgrade
import tests
import tests.fixtures.project
import tests.fixtures.requirements

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


AVAILABLE_POST = """
utila (2.97.0.post5+7356925)  - 2.97.0.post5+7356925
  INSTALLED: 2.97.0
  LATEST:    2.97.0.post5+7356925
"""


def test_available_post():
    post = baw.cmd.upgrade.available_version(AVAILABLE_POST)
    assert post == "2.97.0.post5+7356925"


@tests.longrun
def test_new_requirements():
    result = baw.cmd.upgrade.determine_new_requirements(
        baw.ROOT,
        tests.fixtures.requirements.REQUIREMENTS,
    )
    # utila should allways be new than 0.5.0
    # assert 'utila' in result[0]
    assert 'PyYAML' in result[0]


TEST_UPGRADE = """\
utila==0.1.0
iamraw
"""

# def test_upgrading(tmpdir):
#     requirements_path = os.path.join(tmpdir, baw.utils.REQUIREMENTS_TXT)
#     baw.utils.file_create(
#         requirements_path,
#         TEST_UPGRADE,
#     )
#     # use default requirements.txt
#     baw.cmd.upgrade.upgrade_requirements(tmpdir)
#     loaded = baw.utils.file_read(requirements_path)
#     assert loaded != TEST_UPGRADE


def test_cmd_upgrade_nopre(simple, capsys):  # pylint:disable=W0621,W0613
    simple[0]('upgrade')
    stdout = tests.stdout(capsys)
    assert 'Start upgrading requirements:' in stdout, stdout
    assert 'Requirements are up to date' in stdout, stdout


def test_cmd_upgrade_pre(simple, capsys):  # pylint:disable=W0621,W0613
    simple[0]('upgrade --pre')
    stdout = tests.stdout(capsys)
    assert 'Start upgrading requirements:' in stdout, stdout
    assert 'Requirements are up to date' in stdout, stdout


# @tests.hasgit
# @tests.nightly
# def test_upgrade_requirements(project_example, capsys):  # pylint: disable=W0613
#     path = project_example

#     def commit_all():
#         completed = baw.runtime.run_target(
#             path,
#             'git add . && git commit -m "Upgrade requirements"',
#         )
#         assert completed.returncode == baw.SUCCESS, str(completed)

#     # yapf in a higher version is provided by dev environment
#     baw.utils.file_append(baw.utils.REQUIREMENTS_TXT, 'yapf==0.10.0')
#     failed_test = textwrap.dedent("""\
#     def test_me():
#         assert 0
#     """)
#     failingtest_path = 'tests/test_failed.py'
#     baw.utils.file_create(failingtest_path, failed_test)
#     commit_all()
#     result = baw.cmd.upgrade.upgrade(
#         path,
#         verbose=True,
#         venv=False,
#         generate=False,  # do not change - see test.py/generate_only
#         notests=False,
#     )
#     assert result == baw.FAILURE
#     stdout = tests.stdout(capsys)
#     assert stdout
#     assert 'Reset' in stdout, stdout
#     # Reuse venv environment
#     # remove failing test
#     baw.utils.file_remove(failingtest_path)
#     commit_all()
#     result = baw.cmd.upgrade.upgrade(
#         path,
#         verbose=False,
#         venv=False,
#         generate=False,  # see above
#     )
#     assert result == baw.SUCCESS

REQUIREMENTS = """\
# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

selenium==3.141.0 # noauto

pytest_localserver==0.7.0
power==2.22.0
"""


def test_smart_replace_comment():
    replaced = baw.requirements.upgrade.smart_replace(
        REQUIREMENTS,
        old='selenium==3.141.0',
        new='selenium==4.4.3',
    )
    assert replaced != REQUIREMENTS
