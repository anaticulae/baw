# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import re

import baw.config
import baw.project
import baw.utils


def cache_clear():
    baw.config.load.cache_clear()


def coverage_min(root, value: float, can_decrease: bool = False):  # pylint:disable=W0613
    value = int(float(value))
    root = baw.project.determine_root(root)
    path = baw.config.config_path(root)
    content = baw.utils.file_read(path)
    exists = 'coverage_min' in content
    new = f'coverage_min = {value}\n'
    if exists:
        content = re.sub(r'coverage_min[ ]?=[ ]?\d{2,3}', new, content)
    elif '[release]' in content:
        content = content.replace('[release]', f'[release]\n{new}')
    else:
        content += f'[release]\n{new}'
    baw.utils.file_replace(path, content)
    cache_clear()
