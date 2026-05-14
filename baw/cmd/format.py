# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import concurrent.futures
import os

import tomli_w
import utilo

import baw.cmd.utils
import baw.config
import baw.runtime
import baw.utils


def evaluate(args):
    root = baw.cmd.utils.get_root(args)
    result = format_repository(
        root,
        verbose=args.get('verbose', 0),
    )
    return result


def format_repository(root: str, verbose: int = 0):
    for item in (format_python, format_toml, format_imports, format_yaml):
        try:
            # TODO: MAKE VERBOSE LEVEL GOBAL
            failure = item(root, verbose=verbose)
        except TypeError:
            failure = item(root)
        if failure:
            return failure
    return baw.SUCCESS


def sources(root: str):
    """\
    >>> import baw.project; sources(baw.determine_root(__file__))
    ['tests', 'baw']
    """
    result = []
    for item in 'setup.py tests'.split():
        if not os.path.exists(item):
            continue
        result.append(item)
    result.extend(baw.config.sources(root))
    return result


def format_python(root: str, verbose: int = 0) -> int:
    baw.log('format source')
    if not baw.runtime.installed('yapf', root=root):
        return baw.FAILURE
    yapf = '-i --style=google --no-local-style'
    parallel = '-p' if not baw.utils.testing() else ''
    template_skip = '-e *.tpy'
    todo = []
    for item in sources(root):
        path = os.path.join(root, item)
        if os.path.isfile(path):
            cmd = f'yapf -i {yapf} {path}'
        else:
            cmd = f'yapf -r {yapf} {template_skip} {parallel} {path}'
        todo.append(cmd)
    completed = baw.runtime.runs(
        todo,
        cwd=root,
        workers=len(todo),
        verbose=verbose,
    )
    baw.log('format source: completed')
    return completed


def format_toml(root: str) -> int:
    files = utilo.file_list(
        root,
        include=[
            'toml',
        ],
        recursive=True,
        absolute=True,
    )
    for item in files:
        if '/tmp/' in item:  # nosec:B108
            continue
        if '/venv/' in item:
            continue
        config = baw.utils.load_toml(item)
        content = tomli_w.dumps(config)
        utilo.file_replace(item, content)
    return baw.SUCCESS


def format_yaml(root: str) -> int:
    utilo.log('format yaml')
    cmd = f'yamlfix {root} --exclude="**/build/**" --exclude="**/venv/**"'
    completed = utilo.run(cmd, cwd=root)
    utilo.debug(completed)
    utilo.log('format yaml: completed')
    if completed.stdout.strip():
        utilo.log(completed.stdout)
    if completed.returncode:
        if completed.stderr:
            utilo.error(completed.stderr)
        return completed.returncode
    return baw.SUCCESS


def format_imports(root: str, verbose: int = 0):
    if not baw.runtime.installed('isort', root=root):
        return baw.FAILURE
    project_sources = baw.config.sources(root)
    short = ' -p '.join(project_sources)
    isort: str = ' '.join(ISORT) % short
    cmd = f'isort {isort}'
    completed = format_(
        root,
        cmd=cmd,
        info='sort imports',
        verbose=verbose,
    )
    return completed


ISORT = (
    "-o",
    "pytest",
    '-p',
    '%s',
    "-p",
    "tests",
    "--ot",
    "--sl",  # force single line
    "--ns",  # override default skip of __init__
    "__init__.py",
    "--line-width 999",  # do not break imports
)


def format_(
    root: str,
    cmd: str,
    info: str = 'format source',
    *,
    verbose: int = 0,
):
    baw.log(info)
    folder = baw.config.sources(root)
    # check that `tests` path exists
    testpath = os.path.join(root, 'tests')
    if os.path.exists(testpath):
        folder.append('tests')
    # TODO: LIMIT MAX_WORKERS?
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        waitfor = []
        for item in folder:
            source = os.path.join(root, item)
            cmdx = f'{cmd} {source}'
            waitfor.append(
                executor.submit(
                    baw.runtime.run_target,
                    root=root,
                    cmd=cmdx,
                    cwd=source,
                    verbose=verbose,
                ))
        for future in concurrent.futures.as_completed(waitfor):
            completed = future.result()
            if completed.returncode:
                baw.error(f'error while formatting {completed.stderr}')
                return baw.FAILURE
    baw.log(f'{info}: completed\n')
    return baw.SUCCESS


def extend_cli(parser):
    test = parser.add_parser('format', help='Format code')
    test.add_argument(
        '--imports',
        help='run isort',
        action='store_true',
    )
    test.add_argument(
        '--code',
        help='run yapf',
        action='store_true',
    )
    test.set_defaults(func=evaluate)
