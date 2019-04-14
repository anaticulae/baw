from os import makedirs
from os.path import exists
from os.path import join
from pytest import fixture
from tests import DATA
from textwrap import dedent

from baw.config import PROJECT_PATH
from baw.config import create_config
from baw.config import project_name
from baw.config import sources
from baw.utils import BAW_EXT
from baw.utils import file_create

PROJECT = join(DATA, 'project.config')

assert exists(PROJECT)


def test_loading_project_config():
    short, name = project_name(PROJECT)

    assert short == 'baw'
    assert name == 'Black and White'


def test_write_and_load_config(tmpdir):
    makedirs(join(tmpdir, BAW_EXT))

    expected_short = 'xesey'
    expected_description = 'this is sparta'

    create_config(tmpdir, expected_short, expected_description)

    short, description = project_name(join(tmpdir, PROJECT_PATH))

    assert short == expected_short
    assert description == expected_description


@fixture
def configuration(tmpdir):
    configuration = """\
    [project]
    short = baw
    name = Black and White
    source = abc
        defg

    [tests]
    minimal_coverage = 50
    """
    configuration = dedent(configuration)

    path = join(tmpdir, 'config.cfg')
    file_create(path, configuration)
    return path


def test_with_sourcecode_extention(configuration):
    """Include further directories in the test cov report"""

    expected_sources = ['baw', 'abc', 'defg']

    assert sources(configuration) == expected_sources
