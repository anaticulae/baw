# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""\
    Patches:
        - insert space after version tag
        - Pathlib, use \n instead of windows nl
"""

import datetime
import os
import pathlib
import typing

import baw.git


def changelog_headers(  # pylint:disable=W0613
    owner: str,
    repo_name: str,
    changelog: dict,
    changelog_sections: list,
    **kwargs,
) -> typing.Optional[str]:
    import semantic_release.changelog.changelog
    output = ""
    for section in semantic_release.changelog.changelog.get_changelog_sections(
            changelog,
            changelog_sections,
    ):
        # Add a header for this section
        output += f"\n### {section.capitalize()}\n\n"
        # Add each commit from the section in an unordered list
        for hashid, message in changelog[section]:
            hashid = hashid[0:12]
            # ('c47ffdd2610e91a3849741010757b5d9ed3b5673', '**jenkinsfile:** Use new junit parameter')
            message = message.split(maxsplit=1)[1]
            # lowercase first letter
            message = message[0].lower() + message[1:]
            output += f"* {message} ({hashid})\n"
    return output


def update_changelog_file(version: str, content_to_add: str):
    """Update changelog file with changelog for the release.

    :param version: The release version number, as a string.
    :param content_to_add: The release notes for the version.
    """

    from semantic_release.settings import config
    from semantic_release.settings import logger
    from semantic_release.vcs_helpers import repo

    changelog_file = config.get("changelog_file")
    changelog_placeholder = config.get("changelog_placeholder")
    git_path = pathlib.Path(os.getcwd(), changelog_file)
    if not git_path.exists():
        original_content = "# Changelog\n\n%s\n" % changelog_placeholder
        logger.warning("Changelog file not found: %s - creating it." % git_path)  # pylint:disable=W1201
    else:
        original_content = git_path.read_text()

    if changelog_placeholder not in original_content:
        logger.warning("Placeholder %s not found " % changelog_placeholder +
                       "in changelog file %s - skipping change." % git_path)
        return

    updated_content = original_content.replace(
        changelog_placeholder,
        "\n".join([
            changelog_placeholder,
            "",
            f"## v{version} ({datetime.date.today():%Y-%m-%d})\n",
            content_to_add,
        ]),
    )
    git_path.write_text(updated_content)
    repo.git.add(str(git_path.relative_to(str(repo.working_dir))))


def __patch__():
    import semantic_release.cli
    semantic_release.cli.update_changelog_file = update_changelog_file

    def read_text(self, encoding=None, errors=None):
        """Open the file in text mode, read it, and close the file."""
        with self.open(
                mode='r',
                encoding=encoding,
                errors=errors,
                newline='\n',
        ) as f:  # pylint:disable=C0103
            return f.read()

    def write_text(self, data, encoding=None, errors=None):
        """Open the file in text mode, write to it, and close the file."""
        if not isinstance(data, str):
            raise TypeError('data must be str, not %s' %
                            data.__class__.__name__)
        with self.open(
                mode='w',
                encoding=encoding,
                errors=errors,
                newline='\n',
        ) as f:  # pylint:disable=C0103
            return f.write(data)

    pathlib.Path.read_text = read_text
    pathlib.Path.write_text = write_text


if baw.git.installed():
    __patch__()
