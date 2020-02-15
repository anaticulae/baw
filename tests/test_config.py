# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import textwrap

import pytest

import baw.config
import baw.utils
import tests

PROJECT = os.path.join(tests.DATA, 'project.config')
assert os.path.exists(PROJECT), str(PROJECT)


@pytest.fixture
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
    config = textwrap.dedent(config)

    path = os.path.join(tmpdir, 'config.cfg')
    baw.utils.file_create(path, config)
    return path


def test_config_load():
    short, name = baw.config.project(PROJECT)

    assert short == 'baw'
    assert name == 'Black and White'


def test_config_create_and_load(tmpdir):
    os.makedirs(os.path.join(tmpdir, baw.utils.BAW_EXT))

    expected_short = 'xesey'
    expected_description = 'this is sparta'

    baw.config.create_config(tmpdir, expected_short, expected_description)

    short, description = baw.config.project(
        os.path.join(
            tmpdir,
            baw.config.PROJECT_PATH,
        ))

    assert short == expected_short
    assert description == expected_description


def test_config_defined_subproject_with_source_parameter(configuration):  #pylint: disable=W0621
    """Include further directories in the test cov report and unit testing."""
    # baw main project and `abc` and `defg` as subprojects
    expected_sources = ['baw', 'abc', 'defg']

    assert baw.config.sources(configuration) == expected_sources
