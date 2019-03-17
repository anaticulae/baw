from os import makedirs
from os.path import exists
from os.path import join

from baw.config import create_config
from baw.config import project_name
from baw.config import PROJECT_PATH
from baw.utils import BAW_EXT
from tests import DATA

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


if __name__ == "__main__":
    test_loading_project_config()
    test_write_and_load_conifg()
