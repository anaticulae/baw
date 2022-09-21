# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import typing


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
