# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
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

PROJECT = os.path.join(tests.DATA, '.baw')
assert os.path.exists(PROJECT), str(PROJECT)


@pytest.fixture
def configuration(testdir):
    root = str(testdir)
    config = """\
    [project]
    short = baw
    name = Beta Alpha Omega
    source = abc
        defg

    [release]
    minimal_coverage = 50
    fail_on_finding = True
    """
    config = textwrap.dedent(config)
    path = os.path.join(root, '.baw')
    baw.utils.file_create(path, config)
    return root


def test_config_load():
    short, name = baw.config.project(PROJECT)
    assert short == 'baw'
    assert name == 'Beta Alpha Omega'


def test_config_create_and_load(tmpdir):
    expected_short = 'xesey'
    expected_description = 'this is sparta'
    baw.config.create(tmpdir, expected_short, expected_description)
    short, description = baw.config.project(baw.config.config_path(tmpdir))
    assert short == expected_short
    assert description == expected_description


def test_config_defined_subproject_with_source_parameter(configuration):  #pylint: disable=W0621
    """Include further directories in the test cov report and unit testing."""
    # baw main project and `abc` and `defg` as subprojects
    expected_sources = ['baw', 'abc', 'defg']
    for item in expected_sources:
        os.makedirs(item)
    assert baw.config.sources(configuration) == expected_sources


def test_config_fail_on_finding(configuration):  #pylint: disable=W0621
    root = str(configuration)
    fail = baw.config.fail_on_finding(root)
    assert fail, 'variable is not parsed correctly'
