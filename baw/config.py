from configparser import ConfigParser
from os.path import exists
from os.path import join

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
    with open(output, mode='w', encoding='utf8') as fp:
        cfg.write(fp)
