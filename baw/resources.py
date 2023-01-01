# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Base for generating project. Templates have to be here."""

import os
import time

import baw
import baw.config
import baw.git
import baw.project.version
import baw.utils

FOLDERS = [
    'tests',
    'docs',
    'docs/releases',
]

TEMPLATES = os.path.join(baw.ROOT, 'baw/templates')
assert os.path.exists(TEMPLATES), f'No template-dir {TEMPLATES}'

WORKSPACE_TEMPLATE = os.path.join(TEMPLATES, '.code-workspace')
assert os.path.exists(WORKSPACE_TEMPLATE), f'No template {WORKSPACE_TEMPLATE}'

GIT_IGNORE_TEMPLATE = os.path.join(TEMPLATES, '.gitignore')
assert os.path.exists(GIT_IGNORE_TEMPLATE), f'No gitignore {GIT_IGNORE_TEMPLATE}'  # yapf:disable

RCFILE_PATH = os.path.join(TEMPLATES, '.rcfile')
assert os.path.exists(RCFILE_PATH), f'No rcfile {RCFILE_PATH}'

ISORT_PATH = os.path.join(TEMPLATES, '.isort.cfg')
assert os.path.exists(ISORT_PATH), f'No isort {ISORT_PATH}'

CONFTEST_PATH = os.path.join(TEMPLATES, 'conftest.tpy')
assert os.path.exists(CONFTEST_PATH), f'No testconf {CONFTEST_PATH}'

README = """\
# {{SHORT}}
"""

CHANGELOG = """\
# Changelog

Every noteable change is logged here.

## v0.0.0 initial release
"""

LICENCE = """\
# Licence
"""

BACKLOG_RST = """\
.. _backlog:

backlog
=======
"""

RELEASE_RST = """\
releases
========

Upcomming releases must be planned here. See unplanned features in
:ref:`backlog` to create next release plan.

current
-------

.. toctree::
  :maxdepth: 1

completed
---------

.. toctree::
  :maxdepth: 1

"""

INDEX_RST = """\
Welcome to {{NAME}}
======================================

Progress
--------

.. toctree::
  :maxdepth: 1

  releases/releases
  releases/backlog
  CHANGELOG

Modules
-------

.. toctree::
   :maxdepth: 4

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

"""

COPYRIGHT = """\
#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""

REQUIREMENTS = COPYRIGHT

INIT = COPYRIGHT + """
import os

__version__ = '0.0.0'

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
"""

ENTRY_POINT = """\
entry_points={
            'console_scripts': ['{{SHORT}} = {{SHORT}}.cli:main'],
},
"""

INIT_CMD = COPYRIGHT + """\
import utila
import utila.cli

from {{SHORT}} import __version__

COMMANDS = [] # add additional cmds here

@utila.saveme
def main():
    parser = utila.cli.create_parser(
        COMMANDS,
        version=__version__,
        config=utila.ParserConfiguration(
            outputparameter=True,
            inputparameter=True,
        ),
    )
    args = utila.parse(parser)
    inputpath, output, _ = utila.sources(args)  # pylint:disable=W0612,W0632
    return utila.SUCCESS
"""

MAIN_CMD = COPYRIGHT + """\
from {{SHORT}}.cli import main

if __name__ == "__main__":
    main()
"""

CODE_WORKSPACE = baw.utils.file_read(WORKSPACE_TEMPLATE)
JENKINSFILE = baw.utils.file_read(os.path.join(TEMPLATES, 'Jenkinsfile'))
GITIGNORE = baw.utils.file_read(os.path.join(TEMPLATES, '.gitignore'))
SETUP_PY = baw.utils.file_read(os.path.join(TEMPLATES, 'setup.tpy'))
SETUP_CFG = baw.utils.file_read(os.path.join(TEMPLATES, 'setup.cfg'))
RELEASE_PLAN = baw.utils.file_read(os.path.join(TEMPLATES, 'docs/plan.rst'))

REFACTOR = baw.utils.file_read(os.path.join(TEMPLATES, 'refactor'))

DOC_CONF = baw.utils.file_read(os.path.join(TEMPLATES, 'conf.py'))

ISORT_TEMPLATE = baw.utils.file_read(ISORT_PATH)
CONFTEST_TEMPLATE = baw.utils.file_read(CONFTEST_PATH)

# None copies files
FILES = [
    # ('..code-workspace', CODE_WORKSPACE),
    ('.git/info/exclude', GITIGNORE),
    ('CHANGELOG.md', CHANGELOG),
    ('README.md', README),
    ('docs/index.rst', INDEX_RST),
    ('docs/releases/backlog.rst', BACKLOG_RST),
    ('docs/releases/releases.rst', RELEASE_RST),
    ('tests/__init__.py', COPYRIGHT),
    ('tests/conftest.py', CONFTEST_TEMPLATE),
    (baw.utils.REQUIREMENTS_TXT, REQUIREMENTS),
    # ('setup.py', SETUP_PY),
]


def template_replace(root: str, template: str, **kwargs) -> str:
    """Replace $vars in template

    Args:
        root(str): project root
        template(str): which contains the {{VARS}}
        kwargs(str): list of variables to replace in template
    Returns:
        content of template with replaced vars
    Hint:
        Vars are defined as {{VARNAME}}.
    """
    root = baw.utils.forward_slash(root, save_newline=False)
    short = baw.config.shortcut(root)
    source = baw.config.sources(root)
    name_ = baw.config.name(root)
    version_tag = baw.project.version.determine(root)
    year = str(time.localtime(time.time()).tm_year)

    template = template.replace('{{SHORT}}', short)
    template = template.replace('{{SOURCES}}', ', '.join(source))
    template = template.replace('{{NAME}}', name_)
    template = template.replace('{{VERSION}}', version_tag)
    template = template.replace('{{ROOT}}', root)
    template = template.replace('{{YEAR}}', year)

    for key, value in kwargs.items():
        value = str(value)  # ensure to repace str
        template = template.replace('{{' + key.upper() + '}}', value)
    template = template.strip()
    return template
