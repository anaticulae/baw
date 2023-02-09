# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import baw.cmd.plan
import baw.gix
import baw.utils
import tests

ROOT = baw.ROOT


def test_plan_releases():
    path = baw.cmd.plan.releases(ROOT)
    assert os.path.exists(path), path


def test_plan_current():
    version = baw.cmd.plan.current(ROOT)
    assert '.' in version, version


def test_plan_current_status():
    status = baw.cmd.plan.status(ROOT)
    assert status != baw.cmd.plan.Status.EMPTY


@tests.nightly
def test_plan_code_quality(project_example):
    quality = baw.cmd.plan.code_quality(project_example)
    assert quality
    assert isinstance(quality.rating, float), quality.rating
    assert quality.rating <= 10.0, quality.rating
    assert quality.coverage <= 100.0, quality.coverage


@tests.nightly
def test_plan_init_first_testplan(project_example):
    """Ensure that project init generates first release plan"""
    plan = os.path.join(project_example, 'docs/releases/0.1.0.rst')
    assert os.path.exists(plan), plan
    clean = baw.gix.is_clean(project_example)
    assert clean, clean


@tests.nightly
def test_plan_close_plan(project_example_done):
    workspace = project_example_done
    baw.cmd.plan.close(workspace)
    current_status = baw.cmd.plan.status(workspace)
    assert current_status == baw.cmd.plan.Status.CLOSED, current_status


@tests.nightly
def test_cli_plan_close_current_plan(project_example_done, monkeypatch):
    workspace = project_example_done
    tests.baaw('plan close', monkeypatch)
    current_status = baw.cmd.plan.status(workspace)
    assert current_status == baw.cmd.plan.Status.CLOSED, current_status


@tests.nightly
def test_cli_plan_close_current_plan_and_open_new(
    project_example_done,
    monkeypatch,
):
    workspace = project_example_done

    tests.baaw('plan close', monkeypatch)
    current_status = baw.cmd.plan.status(workspace)
    assert current_status == baw.cmd.plan.Status.CLOSED, current_status

    tests.baaw('plan new', monkeypatch)
    current_status = baw.cmd.plan.status(workspace)
    assert current_status == baw.cmd.plan.Status.OPEN, current_status
