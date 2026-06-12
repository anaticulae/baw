#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import textwrap

import pytest
import utilo

import baw
import baw.cmd.upgrade
import baw.project.version
import baw.requirements.parser
import baw.requirements.upgrade
import baw.runtime
import tests
import tests.fixtures.requirements

NEW_VERSION_AVAILABLE = """
utilo (0.5.4)  - 0.5.4
  INSTALLED: 0.5.3
  LATEST:    0.5.4
"""

AVAILABLE_INSTALLED = """
utilo (0.5.4)  - 0.5.4
  INSTALLED: 0.5.4 (latest)
"""

AVAILABLE_COMPLEX = """
pdfminer.six (20181108)  - 20181108
  INSTALLED: 20181108 (latest)
"""

AVAILABLE_MULTIPLE = """
utilotest (0.1.5)  - 0.1.5
  INSTALLED: 0.1.4
  LATEST:    0.1.5
utilo (2.11.0)     - 2.11.0
"""


def test_complex():
    available = baw.cmd.upgrade.available_version(AVAILABLE_COMPLEX)
    assert available == "20181108"

    installed = baw.cmd.upgrade.installed_version(AVAILABLE_COMPLEX)
    assert installed == "20181108"


def test_available_multiple():
    available = baw.cmd.upgrade.available_version(
        AVAILABLE_MULTIPLE,
        package='utilo',
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
utilo (2.97.0.post5+7356925)  - 2.97.0.post5+7356925
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
    # utilo should allways be new than 0.5.0
    # assert 'utilo' in result[0]
    assert 'PyYAML' in result[0]


TEST_UPGRADE = """\
utilo==0.1.0
iamraw
"""


def test_upgrading(tmpdir):
    requirements_path = utilo.join(tmpdir, baw.utils.REQUIREMENTS_TXT)
    utilo.file_create(
        requirements_path,
        TEST_UPGRADE,
    )
    # use default requirements.txt
    baw.cmd.upgrade.upgrade_requirements_txt(tmpdir)
    loaded = utilo.file_read(requirements_path)
    assert loaded != TEST_UPGRADE


@pytest.mark.xfail
def test_cmd_upgrade_nopre(simple, capsys):  # pylint:disable=W0621,W0613
    simple[0]('upgrade')
    stdout = tests.stdout(capsys)
    assert 'Start upgrading requirements:' in stdout, stdout
    assert 'Requirements are up to date' in stdout, stdout


@pytest.mark.xfail
def test_cmd_upgrade_pre(simple, capsys):  # pylint:disable=W0621,W0613
    simple[0]('upgrade --pre')
    stdout = tests.stdout(capsys)
    assert 'Start upgrading requirements:' in stdout, stdout
    assert 'Requirements are up to date' in stdout, stdout


def test_upgrade_requirements_toml(project_example):
    before = utilo.file_read(utilo.join(project_example, baw.PYPROJECT))
    replaced = baw.cmd.upgrade.upgrade_requirements_toml(project_example)
    assert replaced == utilo.SUCCESS
    after = utilo.file_read(utilo.join(project_example, baw.PYPROJECT))
    assert before != after


def commit_all(path, msg='Upgrade requirements'):
    completed = baw.runtime.run_target(
        path,
        f'git add . && git commit -m "{msg}"',
    )
    assert completed.returncode == utilo.SUCCESS, str(completed)


# yapf in a higher version is provided by dev environment
YAPF = """\
[project.optional-dependencies]
dev = [
    "yapf == 0.10.0",
]

[tool.semantic_release]
"""


@tests.hasgit
@tests.nightly
def test_upgrade_requirements(project_example, capsys):  # pylint: disable=W0613
    path = project_example
    # yapf in a higher version is provided by dev environment
    content = utilo.file_read(utilo.join(path, baw.PYPROJECT))
    content = content.replace('[tool.semantic_release]', YAPF)
    utilo.file_replace(baw.PYPROJECT, content)
    commit_all(path, msg='prepare env for test')
    failed_test = textwrap.dedent("""\
    def test_me():
        assert 0
    """)
    failingtest_path = 'tests/test_failed.py'
    utilo.file_create(failingtest_path, failed_test)
    commit_all(path)
    result = baw.cmd.upgrade.upgrade(
        path,
        verbose=True,
        generate=False,  # do not change - see test.py/generate_only
        notests=False,
    )
    assert result == baw.FAILURE
    stdout = tests.stdout(capsys)
    assert stdout
    assert 'Reset' in stdout, stdout
    # Reuse venv environment
    # remove failing test
    utilo.file_remove(failingtest_path)
    commit_all(path)
    result = baw.cmd.upgrade.upgrade(
        path,
        verbose=False,
        generate=False,  # see above
    )
    assert result == baw.SUCCESS


MINUS = """\
[project.optional-dependencies]
dev = [
    "sphinx-autorun == 1.0.0",
]

[tool.semantic_release]
"""


@tests.hasgit
def test_upgrade_minus_lowerminus(project_example):
    path = project_example
    pyproject = utilo.join(path, baw.PYPROJECT)
    content = utilo.file_read(pyproject)
    content = content.replace('[tool.semantic_release]', MINUS)
    utilo.file_replace(baw.PYPROJECT, content)
    commit_all(path, msg='prepare env for test')
    content = utilo.file_read(pyproject)
    assert "sphinx-autorun == 1.0.0" in content
    tests.run('baw upgrade', cwd=path)
    content = utilo.file_read(pyproject)
    assert "sphinx-autorun==2.0.0" in content


MORE_THAN_ONE_MAJOR = """\
[project.optional-dependencies]
dev = [
    "cryptography>=38.0.0,<47.0.0"
]

[tool.semantic_release]
"""


@tests.hasgit
def test_upgrade_more_than_one_major(project_example):
    """\
    Before this patch:

    dependencies = [
        "cryptography>=38.0.0,<47.0.0",
    ]
    Upgrades to:
        "cryptography>=48.0.0,<47.0.0",
    Instead of:
        "cryptography>=48.0.0,<49.0.0",
    Current max on pypi is 48.0.0
    """
    path = project_example
    pyproject = utilo.join(path, baw.PYPROJECT)
    content = utilo.file_read(pyproject)
    content = content.replace('[tool.semantic_release]', MORE_THAN_ONE_MAJOR)
    utilo.file_replace(baw.PYPROJECT, content)
    commit_all(path, msg='prepare env for test')
    content = utilo.file_read(pyproject)
    assert "cryptography>=38.0.0,<47.0.0" in content
    utilo.run('baw upgrade', cwd=path, live=True)
    content = utilo.file_read(pyproject)
    assert "<47.0.0" not in content
    # assert "cryptography>=48.0.0,<49.0.0" in conten
    item = [
        item.strip()[1:-2]
        for item in content.splitlines()
        if 'cryptography' in item
    ]
    assert item, str(content)
    versions = baw.requirements.parser.line_parse(item[0])
    versions = versions[1]['cryptography'][0]
    major = baw.project.version.major(versions)
    assert major >= 48, versions


REQUIREMENT_DOES_NOT_EXISTS = """\
[project.optional-dependencies]
dev = [
    "cryptography>=138.0.0,<139.0.0"
]

[tool.semantic_release]
"""


@tests.hasgit
def test_upgrade_requirement_does_not_exists(project_example):
    path = project_example
    pyproject = utilo.join(path, baw.PYPROJECT)
    content = utilo.file_read(pyproject)
    content = content.replace('[tool.semantic_release]', REQUIREMENT_DOES_NOT_EXISTS) # yapf:disable
    utilo.file_replace(baw.PYPROJECT, content)
    commit_all(path, msg='prepare env for test')
    content = utilo.file_read(pyproject)
    assert "cryptography>=138.0.0,<139.0.0" in content
    completed = utilo.run('baw upgrade', cwd=path)
    assert '[ERROR] package: cryptography; lower border 138.0.0 is larger ' in completed.stderr


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


def commit_and_release(simple, monkeypatch):
    root = simple[1]

    upgrade = utilo.splitlines("""\
        git config advice.setUpstreamFailure false
        touch ABC
        git add .
        git commit -a -m "feat(hello): this is comm"
    """)

    for cmd in upgrade:
        baw.runtime.run_target(root, cmd)

    content = utilo.file_read(utilo.join(root, baw.PYPROJECT))
    assert 'version = "0.0.0"' in content, content

    tests.baaw(
        'release minor --no_test --no_sync --no_linter --no_push',
        monkeypatch,
    )


@tests.hasbaw
@tests.hasgit
@tests.longrun
def test_upgrade_version_number(simple, monkeypatch):
    root = simple[1]
    commit_and_release(simple, monkeypatch)

    content = utilo.file_read(utilo.join(root, baw.PYPROJECT))
    assert 'version = "0.1.0"' in content, content


@tests.hasbaw
@tests.hasgit
@tests.longrun
def test_upgrade_changelog(simple, monkeypatch):
    root = simple[1]
    commit_and_release(simple, monkeypatch)

    changelog = utilo.file_read(utilo.join(root, 'CHANGELOG'))
    assert 'v0.1.0' in changelog
