"""Handle access to project configuration which is stored in .baw-folder."""
from configparser import ConfigParser
from os.path import exists
from os.path import join

from baw.utils import NEWLINE

PROJECT_PATH = '.baw/project.config'


def config(path: str):
    assert exists(path)
    cfg = ConfigParser()
    with open(path, mode='r') as fp:
        cfg.read_file(fp)
    return cfg


def project_name(path: str):
    assert exists(path)
    cfg = config(path)
    return (cfg['project']['short'], cfg['project']['name'])


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
        return []


def create_config(root: str, shortcut: str, name: str):
    """Create project-config in .baw folder

    Args:
        shortcut(str): short name eg. 3 chars long
        name(str): project-name which is used in generated documents
    """
    assert exists(root)
    cfg = ConfigParser()
    cfg['project'] = {'short': shortcut, 'name': name}
    output = join(root, PROJECT_PATH)
    with open(output, mode='w', encoding='utf8', newline=NEWLINE) as fp:
        cfg.write(fp)
