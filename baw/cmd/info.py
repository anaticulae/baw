# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import configparser
import functools
import os
import re
import sys

import baw
import baw.cmd.image
import baw.cmd.utils
import baw.config
import baw.gix
import baw.project
import baw.runtime
import baw.utils


def evaluate(args: dict):
    root = baw.cmd.utils.get_root(args)
    value = args['info'][0]
    returncode = prints(
        root=root,
        value=value,
        verbose=args.get('verbose', False),
    )
    return returncode


def prints(root, value: str, verbose: bool = False) -> int:  # pylint:disable=R1260,R0911
    if value == 'tmp':
        print_tmp(root)
        return baw.SUCCESS
    if value == 'venv':
        print_venv(root)
        return baw.SUCCESS
    if value == 'covreport':
        print_covreport(root)
        return baw.SUCCESS
    if value == 'requirement':
        baw.log(requirement_hash(
            root,
            verbose=verbose,
        ))
        return baw.SUCCESS
    if value == 'name':
        baw.log(baw.config.name(root))
        return baw.SUCCESS
    if value == 'shortcut':
        baw.log(baw.config.shortcut(root))
        return baw.SUCCESS
    if value == 'sources':
        baw.log(' '.join(baw.config.sources(root) + ['tests']))
        return baw.SUCCESS
    if value == 'pip':
        baw.log(pip_version(root, verbose=verbose))
        return baw.SUCCESS
    if value == 'image':
        baw.log(baw.cmd.image.tag(root))
        return baw.SUCCESS
    if value == 'describe':
        baw.log(baw.gix.describe(root))
        return baw.SUCCESS
    if value == 'stable':
        baw.log(baw.project.version.determine(root, verbose=verbose))
        return baw.SUCCESS
    if value == 'branch':
        baw.log(baw.gix.branchname(root))
        return baw.SUCCESS
    if value == 'cov':
        print_cov()
        return baw.SUCCESS
    if value == 'clean':
        if baw.gix.is_clean(root, verbose=False):
            baw.log('very clean')
            return baw.SUCCESS
        baw.log('not clean\n')
        # log data
        baw.log(baw.runtime.run('git status', root).stdout)
        return baw.FAILURE
    return baw.FAILURE


def print_tmp(root: str):
    name: str = 'global'
    if not baw.config.venv_global():
        root = baw.project.determine_root(root)
        name = os.path.split(root)[1]
    tmpdir = os.path.join(baw.config.bawtmp(), 'tmp', name)
    baw.log(tmpdir)
    sys.exit(baw.SUCCESS)


def pip_version(root: str, verbose: bool = False):
    """\
    >>> import baw;pip_version(baw.ROOT)
    '...'
    >>> pip_version(baw.ROOT, verbose=True)
    'baw==...'
    """
    current = utila.quick.git_hash(root)
    result = current
    if verbose:
        name = utila.baw_name(root)
        result = f'{name}=={result}'
    return result


def print_venv(root: str):
    tmpdir = baw.runtime.virtual(
        root,
        creates=False,
    )
    baw.log(tmpdir)
    sys.exit(baw.SUCCESS)


def print_covreport(root: str):
    result = os.path.join(
        baw.utils.tmp(root),
        'report',
    )
    baw.log(result)
    sys.exit(baw.SUCCESS)


def print_cov() -> int:
    completed = utila.run('baw test --cov --no_report')
    if completed.returncode:
        return completed.returncode
    coverage = re.search(
        r'Total coverage: (?P<coverage>\d{1,3}\.\d{2})',
        completed.stdout,
    )
    if not coverage:
        sys.exit(baw.FAILURE)
    result = float(coverage['coverage'])
    baw.log(result)
    sys.exit(baw.SUCCESS)


def requirement_hash(root: str, verbose: bool = False) -> str:
    """\
    >>> import baw
    >>> requirement_hash(baw.ROOT)
    '...'
    >>> requirement_hash(baw.ROOT, verbose=True)
    'baw:...'
    """
    todo = ('Jenkinsfile requirements.txt requirements.dev '
            'requirements.extra tests/conftest.py').split()
    content = ''
    for fname in todo:
        path = os.path.join(root, fname)
        if not os.path.exists(path):
            continue
        content += baw.utils.file_read(path)
    hashed = str(baw.utils.binhash(content))
    if verbose:
        name = baw.config.shortcut(root)
        hashed = f'{name}:{hashed}'
    return hashed


CHOISES = ('name shortcut sources venv tmp '
           'covreport requirement image clean describe stable '
           'branch pip cov').split()


def extend_cli(parser):
    info = parser.add_parser('info', help='Print project information')
    info.add_argument(
        'info',
        help='Print project information',
        nargs=1,
        choices=CHOISES,
    )
    info.set_defaults(func=evaluate)


def baw_name(path: str) -> str:
    """\
    >>> baw_name(__file__)
    'utilo'
    """
    config = baw_config(path)
    if not config:
        return None
    return config.get("project").get("short")


BAW = ".baw"


@functools.lru_cache
def baw_config(path: str) -> dict:
    """\
    >>> baw_config(__file__)
    {'project': {'short': 'utilo', 'name': 'write it once'},...'test': {'plugins': 'timeout'}}
    """
    root = baw_root(path)
    if not root:
        return None
    config = join(root, BAW)
    result = load_config(config)
    return result


def baw_root(path: str) -> str:
    """Go upwards till project config file occurs.

    >>> baw_root(__file__)
    '...'
    """
    current = str(path)
    while not baw.exitx(join(current, BAW)):  # pylint:disable=W0149
        current, base = os.path.split(current)
        if not str(base).strip():
            # root of file sytem
            return None
    return current


def join(*items, exist: bool = False, assert_exists: bool = False) -> str:
    """\
    >>> join('hello', 'tello/well', 'wello')
    'hello/tello/well/wello'
    """
    path = os.path.join(*items)
    path = baw.forward_slash(path)
    exist |= assert_exists
    assert not exist or os.path.exists(path), path
    return path


def load_config(raw: str, flat: bool = False) -> dict:
    r"""Load configuration from string.

    >>> load_config('[rawmaker]\nchar_margin = 10\nline_margin = 10.0')
    {'rawmaker': {'char_margin': '10', 'line_margin': '10.0'}}
    >>> load_config('first = 1\nsecond=2', flat=True)
    {'first': '1', 'second': '2'}
    """
    raw = from_raw_or_path(raw, ftype="ini")
    config = configparser.ConfigParser(allow_no_value=True)
    try:
        config.read_string(raw)
    except configparser.MissingSectionHeaderError:
        # support formats without any section
        raw = f"[DEFAULT]\n{raw}"
        config.read_string(raw)
    result = {}
    for section, keys in config.items():
        level = {}
        for key in keys:
            level[key] = config[section][key]
        result[section] = level

    if flat:
        return result["DEFAULT"]
    del result["DEFAULT"]
    return result


def from_raw_or_path(
    content: str,
    ftype: str = "yaml",
    fname: str = None,
) -> str:
    """Provide raw content from file or pass content

    This method enables the interface to get content from filepath,
    directory or use direct raw content.

    Args:
        content(str): filepath or raw content
        ftype(str): file type which is checked
        fname(str): if `content` is directory, and ``directory/fname.ftype``
                    exists, load ``directory/fname.ftype``
    Returns:
        loaded content or raw passed content
    Raises:
        FileNotFoundError: if `content` path not exists
    """
    content = str(content)  # convert `LocalPath` to str
    if content.endswith(f".{ftype}") and not os.path.exists(content):
        raise FileNotFoundError(f"file not exists: {content}")
    try:
        isdir = baw.NEWLINE not in content and os.path.isdir(content)
    except ValueError:
        # File name is too long, cause testing yaml content as file content.
        isdir = False
    if fname and isdir:
        # use default file path if exists
        if newpath := baw.file_find(content, fnames=fname, ftype=ftype):
            content = newpath
        else:
            raise FileNotFoundError(
                "directory not found: " f"{content} {fname} {ftype}"
            )
    # filepath must not have any line breaks
    if len(content.splitlines()) == 1 and os.path.isfile(content):
        content = baw.file_read(content)
    return content
