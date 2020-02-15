# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Handle access to project configuration which is stored in .baw-folder."""
import configparser
import os
import typing

import baw.utils

PROJECT_PATH = [
    '.baw/project.cfg',
    '.baw/project.config',  # legacy
]


def name(root: str):
    assert os.path.exists(root)
    path = config_path(root)
    _, name_ = project(path)
    # escape '
    name_ = name_.replace("'", r'\'')
    return name_


def shortcut(root: str) -> str:
    """Read short project name out of project config.

    Args:
        root(str): path to project root
    Returns:
        shortname of the project
    """
    assert os.path.exists(root)
    path = config_path(root)
    short, _ = project(path)
    return short


def create(root: str, shortname: str, longname: str):
    """Create project-config in .baw folder

    Args:
        root(str): path to expected project root
        shortname(str): short name eg. 3 chars long of project
        longname(str): project-name which is used in generated
    """
    assert os.path.exists(root)
    cfg = configparser.ConfigParser()
    cfg['project'] = {'short': shortname, 'name': longname}
    outpath = config_path(root)
    with open(
            outpath,
            mode='w',
            encoding=baw.utils.UTF8,
            newline=baw.utils.NEWLINE,
    ) as fp:
        cfg.write(fp)


def commands(root: str) -> dict:
    """Determine commands to run out of project config.

    Args:
        root(str): project root
    Returns:
        dict{name, command}: dict with commands to execute
    """
    assert os.path.exists(root), root

    path = config_path(root)
    assert os.path.exists(path), path
    cfg = load(path)
    try:
        # TODO: DIRTY, goto standard lib
        return {item: cfg['run'][item] for item in cfg['run']}
    except KeyError:
        return {}


def minimal_coverage(root: str) -> int:
    """Read percentage of required test coverage

    Args:
        root(str): path to project root
    Returns:
        percentage of required test coverage
    """
    assert os.path.exists(root)
    path = config_path(root)
    cfg = load(path)

    try:
        min_coverage = int(cfg['tests']['minimal_coverage'])
    except KeyError:
        min_coverage = 20
    return min_coverage


def load(path: str):
    if not os.path.exists(path):
        raise ValueError('Configuration %s does not exists' % path)
    cfg = configparser.ConfigParser()
    with open(path, mode='r', encoding=baw.utils.UTF8) as fp:
        cfg.read_file(fp)
    return cfg


def project(path: str) -> typing.Tuple[str, str]:
    """Determine tuple of `shortcut` and `project name` current `path`
    project.

    Args:
        path to configuration file
    Returns:
        tuple of shortcut and project name
    """
    assert os.path.exists(path), str(path)
    cfg = load(path)
    return (cfg['project']['short'], cfg['project']['name'])


def sources(root: str) -> list:
    """Read `source` form configuration `path`.

    Args:
        root(str): path to project configuration
    Returns:
        list with source folder of project
    """
    # support accessing the config directly or due the project path
    if os.path.isfile(root):
        path = root
    else:
        path = config_path(root)
    assert os.path.exists(path), path
    cfg = load(path)
    try:
        source = cfg['project']['source'].splitlines()
    except KeyError:
        source = []
    source.insert(0, cfg['project']['short'])
    return source


def config_path(root: str) -> str:
    """Select configuration path based on project `root`. If no paths
    exists return prefered expected path."""
    for item in PROJECT_PATH:
        expected = os.path.join(root, item)
        if os.path.exists(expected):
            return expected
    # if no path exists, return default one
    return os.path.join(root, PROJECT_PATH[0])
