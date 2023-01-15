# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import difflib

import baw.requirements
import baw.requirements.check
import baw.utils


def replace(requirements: str, update: 'NewRequirements') -> str:
    for package, [old, new] in update.equal.items():
        # no version was given for old package
        pattern = f'{package}'
        if old:
            pattern += f'=={old}'
        replacement = f'{package}=={new}'
        baw.utils.log(f'replace requirement:\n{pattern}\n{replacement}')
        requirements = smart_replace(requirements, pattern, replacement)
    for package, [old, new] in update.greater.items():
        if isinstance(old, str):
            if baw.requirements.check.lower(old, new):
                # skip lower version
                continue
            pattern = f'{package}>={old}'
            replacement = f'{package}>={new}'
        else:
            if baw.requirements.check.lower(old[0], new):
                # skip lower version
                continue
            # TODO: first approach of greater equal replacement
            pattern = f'{package}>={old[0]}<{old[1]}'
            replacement = f'{package}>={new}<{old[1]}'
        if pattern == replacement:
            continue
        baw.utils.log(f'replace requirement:\n{pattern}\n{replacement}')
        requirements = smart_replace(requirements, pattern, replacement)
    return requirements


def smart_replace(requirements: str, old: str, new: str):
    """Ensure that `PyYAML==5.1.0` matches with `PyYAML==5.1` as `old`
    requirement line."""
    result = [
        line if not line_match(line, old) else line.replace(old, new)
        for line in requirements.splitlines()
    ]
    result = baw.utils.NEWLINE.join(result) + baw.utils.NEWLINE
    assert requirements != result, f'replacement does not work: {old}; {new}; {requirements}'
    return result


def line_match(line, old) -> bool:
    """\
    >>> line_match('selenium==3.141.0 # noauto', 'selenium==3.141.0')
    True
    >>> line_match('selenium==4.4.3', 'selenium==3.141.0')
    False
    """
    line = line.split('#')[0]  # remove optional comment
    if difflib.get_close_matches(
            line,
        [old],
            n=1,
            cutoff=0.9,
    ):
        return True
    return False


def diff(
    current: 'Requirements',
    requested: 'Requirements',
    minimal: bool = False,
):
    # TODO: SUPPORT GREATER THAN
    result = baw.requirements.Requirements()
    for key, value in requested.equal.items():
        with contextlib.suppress(KeyError):
            if current.equal[key] == value:
                continue
        result.equal[key] = value  # pylint:disable=E1137
    for key, value in requested.greater.items():
        with contextlib.suppress(KeyError):
            if minimal:
                value = value[0], value[0]
            if baw.requirements.check.inside(current.equal[key], value):
                continue
            if minimal:
                value = value[0]
        result.greater[key] = value  # pylint:disable=E1137
    return result
