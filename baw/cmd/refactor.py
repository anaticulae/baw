# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import re
import sys

import utila

import baw.cmd.utils
import baw.git
import baw.utils


def run(
    root: str,
    verbose: bool = True,
):
    if not baw.git.is_clean(root, verbose=False):
        baw.utils.error(f'clean before refactor: {root}')
        sys.exit(baw.utils.FAILURE)
    changed = pattern_run(
        root,
        verbose=verbose,
    )
    if changed:
        baw.git.commit(
            root,
            source='.',
            message='refactor(replace): automated replacement',
            verbose=False,
        )
    else:
        baw.utils.log('nothing todo')
    sys.exit(baw.utils.SUCCESS)


TODO = """\
assert_type_list(                            asserts_types(
iflatten(                                    iflat(
intersecting_rectangle(                      rect_intersecting(
intersecting_rectangle_cluster(              rect_intersecting_cluster(
islist(                                      iterable(
level_temp(                                  level_tmp(
log_stacktrace(                              print_stacktrace(
make_unique(                                 unique(
manhatten(                                   manhattan(
not_none(                                    notnone(
parse_numbers(                               parse_ints(
ranged_list(                                 rlist(
ranged_tuple(                                rtuple(
rectangle_border_points(                     rect_border_points(
rectangle_center(                            rect_center(
rectangle_ensure_bounding(                   rect_ensure_bounding(
rectangle_height(                            rect_height(
rectangle_height(                            rect_height(
rectangle_inside(                            rect_inside(
rectangle_intersecting(                      rect_intersecting(
rectangle_max(                               rect_max(
rectangle_merge(                             rect_merge(
rectangle_overlapping(                       rect_overlapping(
rectangle_roundsmall(                        rect_roundsmall(
rectangle_scale(                             rect_scale(
rectangle_size(                              rect_size(
rectangle_width(                             rect_width(
utila.flatten(                               utila.flat(
yaml_from_raw_or_path(                       yaml_load(

FixedFooterInformation(                      FixedFooterInfo(
FixedHeaderInformation(                      FixedHeaderInfo(
FootRawNote(                                 FootNoteRaw(
FooterInformation(                           FooterInfo(
HeaderInformation(                           HeaderInfo(
MovingFooterInformation(                     MovingFooterInfo(
PagesFooterInformation(                      PagesFooterInfo(

typing.List                                  list
typing.Tuple                                 tuple
typing.Dict                                  dict

typing.Iterable                              collections.abc.Iterable
"""


def pattern_run(root: str, verbose: bool) -> bool:
    splitted = todo()
    changed = False
    for path in files(root):
        content = baw.utils.file_read(path)
        before = hash(content)
        for key, value in splitted.items():
            content = content.replace(key, value)
        if hash(content) != before:
            if verbose:
                baw.utils.log(f'refactor: {path}')
            changed = True
        baw.utils.file_replace(path, content)
    return changed


def todo() -> dict:
    """\
    >>> len(todo()) > 10
    True
    """
    result = {}
    for line in TODO.splitlines():
        line = line.strip()
        if not line:
            continue
        splitted = re.split(r'(.*?)[ ]{10,}(.*?)', line)
        result[splitted[1]] = splitted[3]
    return result


def files(root: str) -> list:
    collected = utila.file_list(
        path=root,
        include='py',
        recursive=True,
        absolute=True,
    )
    result = []
    for path in collected:
        if 'build' in path:
            continue
        result.append(path)
    return result


def evals(args: dict):
    root = baw.cmd.utils.get_root(args)
    baw.utils.log(f'refactor: {root}')
    run(root=root,)


def extend_cli(parser):
    created = parser.add_parser(
        'refactor',
        help='Run refactor',
    )
    created.set_defaults(func=evals)
