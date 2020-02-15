# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from os import makedirs
from os.path import exists
from os.path import join
from textwrap import dedent

from pytest import fixture

from baw.config import PROJECT_PATH
from baw.config import create_config
from baw.config import project_name
from baw.config import sources
from baw.utils import BAW_EXT
from baw.utils import file_create
from tests import DATA

PROJECT = join(DATA, 'project.config')

assert exists(PROJECT)


@fixture
def configuration(tmpdir):
    config = """\
    [project]
    short = baw
    name = Black and White
    source = abc
        defg

    [tests]
    minimal_coverage = 50
    """
    config = dedent(config)

    path = join(tmpdir, 'config.cfg')
    file_create(path, config)
    return path


def test_config_load():
    short, name = project_name(PROJECT)

    assert short == 'baw'
    assert name == 'Black and White'


def test_config_create_and_load(tmpdir):
    makedirs(join(tmpdir, BAW_EXT))

    expected_short = 'xesey'
    expected_description = 'this is sparta'

    create_config(tmpdir, expected_short, expected_description)

    short, description = project_name(join(tmpdir, PROJECT_PATH))

    assert short == expected_short
    assert description == expected_description


def test_config_defined_subproject_with_source_parameter(configuration):  #pylint: disable=W0621
    """Include further directories in the test cov report and unit testing."""
    # baw main project and `abc` and `defg` as subprojects
    expected_sources = ['baw', 'abc', 'defg']

    assert sources(configuration) == expected_sources
