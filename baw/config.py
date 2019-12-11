"""Handle access to project configuration which is stored in .baw-folder."""
from configparser import ConfigParser
from os.path import exists
from os.path import isfile
from os.path import join

from baw.utils import NEWLINE
from baw.utils import UTF8

PROJECT_PATH = '.baw/project.config'


def config(path: str):
    if not exists(path):
        raise ValueError('Configuration %s does not exists' % path)
    cfg = ConfigParser()
    with open(path, mode='r', encoding=UTF8) as fp:
        cfg.read_file(fp)
    return cfg


def project_name(path: str):
    cfg = config(path)
    return (cfg['project']['short'], cfg['project']['name'])


def sources(path: str):
    """Read `source` form configuration `path`

    Args:
        path(str): path to project configuration
    Returns:
        list with source folder of project
    """

    # support accessing the config directly or due the project path
    if not exists(path) or not isfile(path):
        potential_config = join(path, PROJECT_PATH)
        if exists(potential_config) and isfile(potential_config):
            path = potential_config
    cfg = config(path)
    try:
        source = cfg['project']['source'].splitlines()
    except KeyError:
        source = []
    source.insert(0, cfg['project']['short'])
    return source


def shortcut(root: str):
    """Read short project name out of project configuration

    Args:
        path(str): path to project root

    Returns:
        shortname of the project"""
    assert exists(root)
    cfg = join(root, PROJECT_PATH)
    short, _ = project_name(cfg)
    return short


def name(root: str):
    assert exists(root)
    cfg = join(root, PROJECT_PATH)
    _, name_ = project_name(cfg)
    # escape '
    name_ = name_.replace("'", r'\'')
    return name_


def minimal_coverage(root: str):
    """Read percentage of required test coverage

    Args:
        path(str): path to project root

    Returns:
        percentage of required test coverage"""
    assert exists(root)
    cfg = config(join(root, PROJECT_PATH))

    try:
        min_coverage = int(cfg['tests']['minimal_coverage'])
    except KeyError:
        min_coverage = 20
    return min_coverage


def commands(root: str):
    """Determine commands to run out of project config

    Args:
        root(str): project root
    Returns:
        dict{name, command}: dict with commands to execute
    """
    assert exists(root)

    path = join(root, PROJECT_PATH)
    assert exists(path)

    cfg = config(path)
    try:
        # TODO: DIRTY, goto standard lib
        return {item: cfg['run'][item] for item in cfg['run']}
    except KeyError:
        return {}


def create_config(root: str, shortname: str, longname: str):
    """Create project-config in .baw folder

    Args:
        shortcut(str): short name eg. 3 chars long
        name(str): project-name which is used in generated documents
    """
    assert exists(root)
    cfg = ConfigParser()
    cfg['project'] = {'short': shortname, 'name': longname}
    output = join(root, PROJECT_PATH)
    with open(output, mode='w', encoding=UTF8, newline=NEWLINE) as fp:
        cfg.write(fp)
