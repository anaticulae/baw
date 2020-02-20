#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
import os
import textwrap

import baw.cmd.upgrade
import baw.requirements
import tests.fixtures.requirements
from baw.cmd.upgrade import available_version
from baw.cmd.upgrade import determine_new_requirements
from baw.cmd.upgrade import installed_version
from baw.cmd.upgrade import upgrade_requirements
from baw.runtime import run_target
from baw.utils import FAILURE
from baw.utils import REQUIREMENTS_TXT
from baw.utils import ROOT
from baw.utils import SUCCESS
from baw.utils import file_append
from baw.utils import file_create
from baw.utils import file_read
from baw.utils import file_remove
from tests import skip_longrun
from tests import skip_nonvirtual
from tests.fixtures.project import project_example  # pylint: disable=W0611

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


@skip_longrun
def test_new_requirements():
    result = determine_new_requirements(
        ROOT,
        tests.fixtures.requirements.REQUIREMENTS,
    )
    # utila should allways be new than 0.5.0
    assert 'utila' in result[0]


TEST_UPGRADE = """\
utila==0.1.0
iamraw
"""


def test_upgrading(tmpdir):
    requirements_path = os.path.join(tmpdir, REQUIREMENTS_TXT)

    file_create(requirements_path, TEST_UPGRADE)

    # use default requirements.txt
    upgrade_requirements(tmpdir, virtual=True)

    loaded = file_read(requirements_path)
    assert loaded != TEST_UPGRADE


@skip_longrun
@skip_nonvirtual
def test_upgrade_requirements(project_example, capsys):  # pylint: disable=W0621, W0613
    path = os.getcwd()

    def commit_all():
        completed = run_target(
            path,
            'git add . && git commit -m "Upgade requirements"',
        )
        assert completed.returncode == SUCCESS, str(completed)

    # yapf in a higher version is provided by dev environment
    file_append(REQUIREMENTS_TXT, 'yapf==0.10.0')

    failed_test = textwrap.dedent("""\
    def test_me():
        assert 0
    """)
    failingtest_path = 'tests/test_failed.py'

    file_create(failingtest_path, failed_test)
    commit_all()

    result = baw.cmd.upgrade.upgrade(
        path,
        verbose=True,
        virtual=True,
        generate=False,  # do not change - see test.py/generate_only
    )
    assert result == FAILURE
    stdout = capsys.readouterr().out

    assert stdout
    assert 'Reset' in stdout, stdout

    # Reuse virtual environment
    # remove failling test
    file_remove(failingtest_path)
    commit_all()

    result = baw.cmd.upgrade.upgrade(
        path,
        verbose=False,
        virtual=True,
        generate=False,  # see above
    )
    assert result == SUCCESS
