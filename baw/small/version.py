# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import sys


def main():
    import baw.config
    import baw.project
    hvcs = baw.config.hvcs(baw.project.determine_root(path=os.getcwd()))
    # TODO: REMOVE LATER
    if hvcs == 'gitea':
        enable_http()
    import semantic_release.cli

    # run the patch
    import baw.changelog  # pylint:disable=W0611

    # rewrite argv
    sys.argv[0] = 'semantic_release'
    # invoke semantic release
    semantic_release.cli.entry()


def enable_http():
    """TODO: REMOVE AFTER SETUP HTTPS."""
    import semantic_release.hvcs
    import semantic_release.vcs_helpers
    before = semantic_release.hvcs.Gitea.api_url

    def api_url():
        return before().replace('https://', 'http://')

    semantic_release.hvcs.Gitea.api_url = api_url

    def push_new_version(
        auth_token: str = None,
        owner: str = None,
        name: str = None,
        branch: str = "master",
        domain: str = "github.com",
    ):
        from git import GitCommandError
        from git import GitError
        from semantic_release.settings import config
        from semantic_release.vcs_helpers import repo
        server = "origin"
        if auth_token:
            token = auth_token
            if config.get("hvcs") == "gitlab":
                token = "gitlab-ci-token:" + token
            actor = os.environ.get("GITHUB_ACTOR")
            if actor:
                server = f"http://{actor}:{token}@{domain}/{owner}/{name}.git"
            else:
                server = f"http://{token}@{domain}/{owner}/{name}.git"

        try:
            repo().git.push(server, branch)
            repo().git.push("--tags", server, branch)
        except GitCommandError as error:
            message = str(error)
            if auth_token:
                message = message.replace(auth_token, "[AUTH_TOKEN]")
            raise GitError(message) from error

    semantic_release.vcs_helpers.push_new_version = push_new_version
