# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw.cmd.plan
import baw.utils
import tests

ROOT = baw.utils.ROOT


def test_plan_releases():
    path = baw.cmd.plan.releases(ROOT)
    assert os.path.exists(path), path


def test_plan_current():
    version = baw.cmd.plan.current(ROOT)
    assert '.' in version, version


def test_plan_current_status():
    status = baw.cmd.plan.status(ROOT)
    assert status != baw.cmd.plan.Status.EMPTY


@tests.skip_longrun
def test_plan_code_quality():
    quality = baw.cmd.plan.code_quality(ROOT)
    assert quality
    assert isinstance(quality.rating, float), quality.rating
    assert quality.rating <= 10.0, quality.rating
