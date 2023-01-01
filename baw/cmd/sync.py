#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import contextlib
import os
import re
import sys
import urllib.request

from pip import __version__ as pip_version

import baw.cmd.utils
import baw.config
import baw.git
import baw.requirements
import baw.requirements.parser
import baw.requirements.upgrade
import baw.run
import baw.runtime
import baw.utils


def sync(
    root: str,
    packages: str = 'dev',
    *,
    minimal: bool = False,
    venv: bool = False,
    verbose: bool = False,
) -> int:
    """Sync packages which are defined in requirements.txt
    Args:
        root(str): root path of project to sync
        packages(str): decide which packages should be synchronized:
                        - dev/ minimal dev environment, formater, linter, test
                        - doc/ Sphinx
                        - extra
                        - all
        minimal(bool): if True use minimal version in requirement file
        venv(bool): if True sync the venv environment
                       if BOTH sync venv and local environment
                       if False sync local environment
        verbose(bool): if True, increase verbosity of logging
    Returns:
        summed exit code of sync processes
    """
    baw.utils.check_root(root)
    ret = 0
    baw.utils.log()
    ret += baw.git.update_gitignore(root, verbose=verbose)
    # NOTE: Should we use Enum?
    if venv == 'BOTH':
        for item in [True, False]:
            ret += sync_dependencies(
                root,
                packages=packages,
                minimal=minimal,
                venv=item,
                verbose=verbose,
            )
            if ret:
                # Fast fail, if one failes, don't check the rest
                return ret
    else:
        ret += sync_dependencies(
            root,
            packages=packages,
            minimal=minimal,
            venv=venv,
            verbose=verbose,
        )
    return ret


def check_dependency(
    root: str,
    package: str,
    *,
    pre: bool = False,
    venv: bool = False,
    verbose: bool = False,
):
    """Check if packages need an upgrade."""
    python = baw.config.python(root, venv=venv)
    for index in sources(pre):
        if not str(index).startswith('http'):
            index = f'http://{index}'
        pip = f'{python} -mpip search --index {index} {package}'
        completed = baw.runtime.run_target(
            root,
            pip,
            verbose=verbose,
            venv=venv,
            skip_error_code=[23, 2],  # package not found
        )
        if completed.returncode == 23:
            # Package not available
            continue
        if completed.returncode == 2:
            baw.utils.error(f'not reachable: {index} for package {package}')
            baw.utils.error(completed.stderr)
            sys.exit(completed.returncode)
            continue
        if completed.returncode and completed.stderr:
            baw.utils.error(completed.stderr)
        if completed.stdout:
            if f'{package} ' not in completed.stdout:
                # nltk (3.5)  - 3.5
                # INSTALLED: 3.5 (latest)
                # skip finding nltk_data when searching for nltk
                continue
            return completed.stdout
    raise ValueError(f'Could not check dependencies {package}')


def sources(pre: bool = False) -> tuple:
    if pre:
        return (baw.config.package_testing(),)
    pip_index, extra_url = baw.config.package_address()
    # if not connected(pip_index, extra_url):
    #     msg = f"Could not reach index {pip_index} or {extra_url}"
    #     raise RuntimeError(msg)
    return (pip_index, extra_url)


def sync_dependencies(  # pylint:disable=R1260
    root: str,
    packages: str,
    *,
    minimal: bool = False,
    verbose: bool = False,
    venv: bool = False,
) -> int:
    baw.utils.check_root(root)
    baw.utils.log('sync venv' if venv else 'sync local')
    resources = determine_resources(root, packages)
    pip_index, extra_url = baw.config.package_address()
    if not connected(pip_index, extra_url):
        baw.utils.error('could not reach package index')
        return baw.utils.FAILURE
    required = required_installation(
        root,
        resources,
        minimal=minimal,
        verbose=verbose,
        venv=venv,
    )
    if not required.equal and not required.greater:
        return baw.utils.SUCCESS
    testing = baw.config.package_testing()
    baw.utils.log(f'\nrequire update:\n{required}')
    # create temporary requirements file
    requirements = baw.utils.tmpfile()
    baw.utils.file_replace(requirements, str(required))
    if '.post' not in str(required):
        testing = None
    cmd, pip = get_install_cmd(
        root=root,
        to_install=requirements,
        pip_index=pip_index,
        extra_url=extra_url,
        testing_url=testing,
        venv=venv,
        verbose=verbose,
    )
    if verbose:
        baw.utils.log(cmd)
    completed = baw.runtime.run_target(
        root,
        cmd,
        cwd=root,
        verbose=False,
        venv=venv,
    )
    baw.utils.file_remove(requirements)
    returncode = eval_sync(pip, completed, verbose=verbose)
    return returncode


def eval_sync(pip, completed, verbose) -> int:
    if 'NewConnectionError' in completed.stdout:
        baw.utils.error(f'Could not reach server: {pip}')
        return completed.returncode
    if completed.stdout:
        for message in completed.stdout.splitlines():
            if should_skip(message, verbose=verbose):
                continue
            if verbose:
                baw.utils.log(message)
    if completed.returncode and completed.stderr:
        baw.utils.error(completed.stderr)
    baw.utils.log()
    return completed.returncode


def required_installation(
    root,
    txts: list,
    minimal: bool = False,
    venv: bool = False,
    verbose: bool = False,
):
    current = pip_list(root, verbose=verbose, venv=venv)
    requested = [
        baw.requirements.parser.parse(baw.utils.file_read(item))
        for item in txts
    ]
    missing = [
        baw.requirements.upgrade.diff(current, item, minimal)
        for item in requested
    ]
    result = baw.requirements.Requirements()
    for item in missing:
        result.equal.update(item.equal)  # pylint:disable=E1101
        if minimal:
            result.equal.update(item.greater)  # pylint:disable=E1101
        else:
            result.greater.update(item.greater)  # pylint:disable=E1101
    # TODO: REMOVE DUPLICATED
    for key in result.greater:
        with contextlib.suppress(KeyError):
            # remove duplicated requirement out of `equal requirement`
            result.equal.pop(key)
            continue
        baw.utils.log(f'duplicated requirement: {key}')
    return result


def determine_resources(root: str, packages: str) -> list:
    """Determine requirements depending on `packages` choice.

    Args:
        root(str): root of generated project
        packages(str): select package to install
    Returns:
        list of absolute paths to requirements.txt's

    Choices(packages):
        - all: install project, test and doc environment
        - dev: install pytest, pycov etc.
        - doc: install Sphinx requirements
        - requirements: only install project requirements.txt
    """
    resources = []
    requirements_dev = 'baw/sync/dev'
    requirements_doc = 'baw/sync/doc'
    if packages == 'dev':
        resources.append(requirements_dev)
    if packages == 'doc':
        resources.append(requirements_doc)
    if packages == 'all':
        resources.append(requirements_dev)
        resources.append(requirements_doc)
    # Requirements_dev is a `global` file from baw project. This file is not
    # given in child project, it is referenced from global baw. Pay attention
    # to the difference of ROOT (baw) and root(project).
    # make path absolute in project
    resources = [os.path.join(baw.ROOT, to_install) for to_install in resources]
    if packages in {'dev', 'all'}:
        if os.path.exists(os.path.join(root, 'requirements.dev')):
            resources.append(os.path.join(root, 'requirements.dev'))
    if packages in {'extra', 'all'}:
        if os.path.exists(os.path.join(root, baw.utils.REQUIREMENTS_EXTRA)):
            resources.append(os.path.join(root, baw.utils.REQUIREMENTS_EXTRA))
    # local project file
    local_requirement = os.path.join(root, baw.utils.REQUIREMENTS_TXT)
    if os.path.exists(local_requirement):
        resources.append(local_requirement)
    return resources


def get_install_cmd(
    root: str,
    to_install: str,
    verbose: bool,
    pip_index: str,
    extra_url: str,
    testing_url: str,
    venv: bool = False,
):
    trusted = host(pip_index)
    warning = '' if verbose else '--no-warn-conflicts'
    pip = f'--index-url {pip_index} --extra-index-url {extra_url} '
    if testing_url:
        pip += f'--extra-index-url {testing_url} '
    pip += f'--trusted {trusted}'
    config = '--retries 2 --disable-pip-version-check '
    if require_legacy_solver():
        config += '--use-deprecated=legacy-resolver '
    python = baw.config.python(root, venv=venv)
    # prepare cmd
    cmd = f'{python} -mpip install {warning} {pip} '
    cmd += f'-U {config} '
    cmd += f'-r {to_install} '
    return cmd, pip


def require_legacy_solver() -> bool:
    """Older pip version does ot require or support this option."""
    major = baw.project.version.major(pip_version)
    if major < 21:
        return False
    if major == 22:
        # TODO: INVESTIGATE LATER
        return False
    return True


HOST = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')


def host(url: str) -> str:
    """\
    >>> host('http://169.254.149.20:6103')
    '169.254.149.20'
    """
    if searched := HOST.search(url):
        return searched[0]
    return None


def pip_list(
    root,
    verbose: bool = False,
    venv: bool = False,
) -> baw.requirements.Requirements:
    python = baw.config.python(root, venv=venv)
    cmd = f'{python} -mpip list --format=freeze'
    if verbose:
        baw.utils.log(cmd)
    completed = baw.runtime.run_target(
        root,
        cmd,
        cwd=root,
        verbose=False,
        venv=venv,
    )
    if completed.returncode and completed.stderr:
        baw.utils.error(f'{cmd}, {verbose}, {venv}')
        baw.utils.error(completed.stderr)
        sys.exit(completed.returncode)
    content = completed.stdout
    parsed = baw.requirements.parser.parse(content)
    return parsed


def connected(internal: str, external: str) -> bool:
    """Test connect to internal and external server. Send a simple http-request
    and check the resonse.

    Args:
        internal(str): adress of internal pip server
        external(str): adress of external pip server
    Returns:
        True if boths connection are green, if not False
    Hint:
        Log the failure of a connection process also
    """
    result = True
    for item in [internal, external]:
        try:
            with urllib.request.urlopen(item) as response:  # nosec
                response.read()
        except urllib.request.URLError:
            result = False
            baw.utils.error(f'Could not reach: {item}')
    return result


def should_skip(msg: str, verbose: bool = False):
    if not verbose and 'Requirement already' in msg:
        baw.utils.log('.', end='')
        return True
    return False


def run(args: dict):
    root = baw.cmd.utils.run_environment(args)
    venv = args.get('venv', False)
    if venv:
        baw.run.run_venv(args)
    result = sync(
        root=root,
        packages=args.get('packages'),
        minimal=args.get('minimal', False),
        verbose=args.get('verbose', False),
        venv=venv,
    )
    return result


def extend_cli(parser):
    synx = parser.add_parser('sync', help='Synchronize project requirements')
    synx.add_argument(
        '--minimal',
        help='use minimal required requirements',
        action='store_true',
    )
    synx.add_argument(
        'packages',
        help='Sync dependencies. Choices: dev(minimal), doc(sphinx), '
        'packages(requirements.txt only), all(dev, doc, packages)',
        nargs='?',
        const='dev',
        choices=['all', 'dev', 'doc', 'extra', 'requirements'],
    )
    synx.set_defaults(func=run)
