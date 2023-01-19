# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Handle access to project configuration which is stored in .baw-folder.

Parameter
---------

release
~~~~~~~

* coverage_min: do not release with fewer test coverage
* fail_on_finding: if True allow only todo-findings. The build must be
                   free of statical code errors.
"""

import configparser
import contextlib
import functools
import io
import os
import sys

import baw
import baw.project
import baw.resources
import baw.utils

PROJECT_PATH = [
    '.baw',
    '.baw/project.cfg',  # legacy
    '.baw/project.config',  # legacy
]

PYTHON_DEFAULT = 'python'
SPELLING_DEFAULT = False
FAIL_ON_FINDING_DEFAULT = True

COVERAGE_MIN = 20


def venv_global() -> bool:
    """Use global venv.

    >>> str(venv_global())
    '...'
    """
    single = str(os.environ.get('BAW_VENV_GLOBAL', default='')).lower()
    if '1' in single or 'true' in single:
        if baw.utils.testing():
            # do not use global for baw project
            return False
        return True
    return False


def venv_always() -> bool:
    """Always use the venv.

    >>> str(venv_always())
    '...'
    """
    single = str(os.environ.get('BAW_VENV_ALWAYS', default='')).lower()
    if '1' in single or 'true' in single:
        if baw.utils.testing():
            # do not use global for baw project
            return False
        return True
    return False


def gitea_server() -> str:
    """\
    >>> gitea_server()
    '...'
    """
    try:
        server = os.environ['GITEA_SERVER_URL']
    except KeyError:
        baw.utils.error('missing GITEA_SERVER_URL')
        sys.exit(baw.utils.FAILURE)
    else:
        result = str(server)
    return result


def git_author_name() -> str:
    """\
    >>> git_author_name()
    '...'
    """
    try:
        author_name = os.environ['GIT_AUTHOR_NAME']
    except KeyError:
        baw.utils.error('missing GIT_AUTHOR_NAME')
        sys.exit(baw.utils.FAILURE)
    else:
        result = str(author_name)
    return result


def git_author_email() -> str:
    """\
    >>> git_author_email()
    '...'
    """
    try:
        author_email = os.environ['GIT_AUTHOR_EMAIL']
    except KeyError:
        baw.utils.error('missing GIT_AUTHOR_EMAIL')
        sys.exit(baw.utils.FAILURE)
    else:
        result = str(author_email)
    return result


def docker_testing() -> str:
    """\
    >>> docker_testing()
    '...'
    """
    try:
        server = os.environ['CAELUM_DOCKER_TEST']
    except KeyError:
        baw.utils.error('missing CAELUM_DOCKER_TEST')
        sys.exit(baw.utils.FAILURE)
    else:
        server = str(server)
    return server


def docker_runtime() -> str:
    """\
    >>> docker_runtime()
    '...'
    """
    try:
        host = os.environ['CAELUM_DOCKER_RUNTIME']
    except KeyError:
        baw.utils.error('missing CAELUM_DOCKER_RUNTIME')
        sys.exit(baw.utils.FAILURE)
    else:
        host = str(host)
    return host


def docker_setup(root: str) -> str:
    """\
    >>> import baw.project
    >>> docker_setup(baw.project.determine_root(__file__)) is None
    True
    """
    result = default_config(
        root,
        lambda x: x['docker']['setup'],
        default=None,
    )
    return result


@functools.lru_cache
def name(root: str):
    assert os.path.exists(root)
    path = config_path(root)
    _, name_ = project(path)
    # escape '
    name_ = name_.replace("'", r'\'')
    return name_


@functools.lru_cache
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
    # cfg['release'] = {'fail_on_finding': True}
    outpath = config_path(root)
    # write to buffer
    output = io.StringIO()
    cfg.write(output)
    output.seek(0)
    content = baw.resources.COPYRIGHT + output.getvalue()
    # create config
    baw.utils.file_replace(outpath, content)


def project_tmpdir(root: str, ensure: bool = True) -> str:
    tmpdir = os.path.join(bawtmp(), 'tmp')
    shortname = shortcut(root)
    path = os.path.join(tmpdir, shortname)
    if ensure:
        os.makedirs(path, exist_ok=True)
    return path


def cmds(root: str) -> dict:
    """Determine cmds to run out of project config.

    Args:
        root(str): project root
    Returns:
        dict{name, cmd}: dict with cmds to execute
    """
    assert os.path.exists(root), root
    path = config_path(root)
    assert os.path.exists(path), path
    cfg = load(path)
    try:
        run = cfg['run']
    except KeyError:
        return {}
    else:
        result = dict(run.items())
    return result


def coverage_min(root: str) -> int:
    """Read percentage of required test coverage

    Args:
        root(str): path to project root
    Returns:
        percentage of required test coverage

    >>> coverage_min(__file__)
    40
    """
    root = baw.project.determine_root(root)
    result = default_config(
        root,
        lambda x: x['release']['coverage_min'],
        default=COVERAGE_MIN,
    )
    if int(str(result)) == COVERAGE_MIN:
        # legacy, TODO: REMOVE LATER
        result = default_config(
            root,
            lambda x: x['release']['minimal_coverage'],
            default=COVERAGE_MIN,
        )
    result = int(str(result))
    return result


def fail_on_finding(root: str) -> bool:
    """Let release fail when build contain statical code errors."""
    result = default_config(
        root,
        lambda x: x['release']['fail_on_finding'],
        default=FAIL_ON_FINDING_DEFAULT,
    )
    return result


@functools.lru_cache
def load(path: str):
    if not os.path.exists(path):
        raise ValueError(f'Configuration {path} does not exists')
    cfg = configparser.ConfigParser()
    with open(path, mode='r', encoding=baw.utils.UTF8) as fp:
        cfg.read_file(fp)
    return cfg


@functools.lru_cache
def project(path: str) -> tuple[str, str]:
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

    >>> sources(__file__)
    ['baw']

    Args:
        root(str): path to project configuration
    Returns:
        list with source folder of project
    """
    # support accessing the config directly or due the project path
    assert os.path.exists(root), root
    root = baw.project.determine_root(root)
    path = config_path(root)
    assert os.path.exists(path), path
    cfg = load(path)
    assert 'tests' not in cfg, 'use `test` instead of `tests`'
    try:
        assert 'sources' not in cfg['project'], '`source` instead of `sources`'
        source = cfg['project']['source'].splitlines()
    except KeyError:
        source = []
    if any(',' in item for item in source):
        baw.utils.error(f'invalid {source} in {path}, remove collon')
        sys.exit(baw.utils.FAILURE)
    failure = 0
    for subproject in source:
        if os.path.exists(os.path.join(root, subproject)):
            continue
        failure += 1
        baw.utils.log(f'subproject does not exists: {subproject}')
    if failure:
        sys.exit(baw.utils.FAILURE)
    # put project name to the front
    source.insert(0, cfg['project']['short'])
    return source


@functools.lru_cache
def config_path(root: str) -> str:
    """Select configuration path based on project `root`.

    If no paths exists return prefered expected path.
    """
    for item in PROJECT_PATH:
        expected = os.path.join(root, item)
        if os.path.exists(expected) and os.path.isfile(expected):
            # isfile: to skip .baw-folder
            return expected
    # if no path exists, return default one
    return os.path.join(root, PROJECT_PATH[0])


@functools.lru_cache
def python(root: str, venv: bool = False) -> str:
    if venv:
        return 'python'
    result = default_config(
        root,
        lambda x: x['project']['python'],
        default=PYTHON_DEFAULT,
    )
    return result


def spelling(root: str) -> bool:
    """\
    >>> spelling(baw.ROOT)
    False
    """
    result = default_config(
        root,
        lambda x: x['project']['spelling'],
        default=SPELLING_DEFAULT,
    )
    return result


def pylint(root: str) -> bool:
    result = default_config(
        root,
        lambda x: x['project']['pylint'],
        default='',
    )
    return result


def pylint_spelling() -> str:
    try:
        result = os.environ['PYLINT_SPELLING']
    except KeyError:
        baw.utils.error('require global env: `PYLINT_SPELLING`')
        sys.exit(baw.utils.FAILURE)
    return result


def plugins(root: str) -> bool:
    result = default_config(
        root,
        lambda x: x['test']['plugins'],
        default='',
    )
    return result


def docker_image(root: str) -> bool:
    """\
    >>> import baw
    >>> docker_image(baw.ROOT)
    '...'
    """
    result = default_config(
        root,
        lambda x: x['docker']['image'],
        default=f'baw:{baw.__version__}',
    )
    return result


def pip_parallel_worker(root: str) -> bool:
    """\
    >>> import baw
    >>> pip_parallel_worker(baw.ROOT) >=1
    True
    """
    parallel_pip_calls = int(os.environ.get('BAW_PARALLEL_PIP_CALLS', '10'))
    result = default_config(
        root,
        lambda x: x['pip']['worker'],
        default=parallel_pip_calls,
    )
    return result


def package_address():
    """\
    >>> package_address()
    ('http...', 'http...')
    """
    try:
        internal = os.environ['PIP_INDEX_URL']
        external = os.environ['PIP_EXTRA_INDEX_URL']
        return (internal, external)
    except KeyError as failure:
        baw.utils.error(f'Missing global var {failure}')
        sys.exit(baw.utils.FAILURE)


def package_testing():
    """\
    >>> package_testing()
    '...'
    """
    try:
        pre = os.environ['PIP_PRE_INDEX_URL']
        return pre
    except KeyError as failure:
        baw.utils.error(f'Missing global var {failure}')
        sys.exit(baw.utils.FAILURE)


def changelog(root: str) -> str:
    """\
    >>> import baw.project
    >>> changelog(baw.project.determine_root(__file__))
    'CHANGELOG'
    """
    for fname in 'CHANGELOG CHANGELOG.md'.split():
        path = os.path.join(root, fname)
        if os.path.exists(path):
            return fname
    raise ValueError(f'could not locate changelog: {root}')


def version(root: str) -> str:
    """\
    >>> import baw.project
    >>> version(baw.project.determine_root(__file__))
    'baw/__init__.py:__version__'
    """
    path = os.path.join(root, 'VERSION')
    if os.path.exists(path):
        return 'VERSION:__version__'
    short = shortcut(root)
    result = f'{short}/__init__.py:__version__'
    return result


def basic(root: str) -> bool:
    """A python project is the default baw project, but also other
    languages are possible.

    >>> import baw.project
    >>> basic(baw.project.determine_root(__file__))
    True
    """
    if 'VERSION' in version(root):
        return False
    return True


def default_config(root: str, access: callable, default=None) -> bool:
    path = root if os.path.isfile(root) else config_path(root)
    if not os.path.exists(path):
        return default
    cfg = load(path)
    with contextlib.suppress(KeyError):
        return access(cfg)
    return default


@functools.lru_cache(maxsize=1)
def bawtmp():
    try:
        path = os.environ['BAW']
    except KeyError:
        baw.utils.error('DEFINE $BAW ENV VAR')
        sys.exit(baw.utils.FAILURE)
    os.makedirs(path, exist_ok=True)
    return path


def docpath(root: str, mkdir: bool = True) -> str:
    shortname = shortcut(root)
    tmpdoc = os.path.join(bawtmp(), 'docs', shortname)
    if mkdir:
        os.makedirs(tmpdoc, exist_ok=True)
    return tmpdoc
