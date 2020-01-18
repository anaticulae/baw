"""Base for generating project. Templates have to be here."""
from os.path import exists
from os.path import join

import baw.project.version
from baw.config import name
from baw.config import shortcut
from baw.config import sources
from baw.git import GIT_REPO_EXCLUDE
from baw.utils import BAW_EXT
from baw.utils import REQUIREMENTS_TXT
from baw.utils import ROOT
from baw.utils import file_read
from baw.utils import forward_slash

FOLDERS = [
    BAW_EXT,
    'tests',
    'docs',
    'docs/releases',
]

TEMPLATES = join(ROOT, 'templates')
assert exists(TEMPLATES), 'No template-dir %s' % TEMPLATES

WORKSPACE_TEMPLATE = join(TEMPLATES, '..code-workspace')
assert exists(WORKSPACE_TEMPLATE), 'No template %s' % WORKSPACE_TEMPLATE

GIT_IGNORE_TEMPLATE = join(TEMPLATES, '.gitignore')
assert exists(GIT_IGNORE_TEMPLATE), 'No gitignore %s' % GIT_IGNORE_TEMPLATE

RCFILE_PATH = join(TEMPLATES, '.rcfile')
assert exists(RCFILE_PATH), 'No rcfile %s' % RCFILE_PATH

ISORT_PATH = join(TEMPLATES, '.isort.cfg')
assert exists(ISORT_PATH), 'No isort %s' % ISORT_PATH

CONFTEST_PATH = join(TEMPLATES, 'conftest.py')
assert exists(CONFTEST_PATH), 'No testconf %s' % CONFTEST_PATH

README = """# {%SHORT%}
"""

CHANGELOG = """# changelog

Every noteable change is logged here.
"""

LICENCE = """# Licence
"""

BUGS_RST = """\
.. _bugs:

bugs
====

open
----

closed
------
"""

CHANGELOG_RST = """.. mdinclude:: ../../CHANGELOG.md
"""

TODO_RST = """\
.. _todo:

todo
====
"""

README_RST = """.. mdinclude:: ../../README.md
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

  0.1.0

completed
---------

.. toctree::
  :maxdepth: 1

"""

INDEX_RST = """Welcome to {%NAME%}
=================================

General
-------

.. toctree::
  :maxdepth: 1

  bugs

Progress
--------

.. toctree::
  :maxdepth: 1

  releases/releases
  releases/backlog
  pages/changelog

Developer
---------

.. toctree::
  :maxdepth: 1

  todo

Modules
--------------------
.. toctree::
   :maxdepth: 4

   .tmp/modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

"""

REQUIREMENTS = ""

COPYRIGHT = """\
#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
"""

INIT = COPYRIGHT + """\
import os

__version__ = '0.0.0'

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
"""

ENTRY_POINT = """\
entry_points={
            'console_scripts': ['{%SHORT%} = {%SHORT%}.cli:main'],
},
"""

INIT_CMD = COPYRIGHT + """\
import utila
import utila.cli

from {%SHORT%} import __version__

COMMANDS = [] # add additional commands here

@utila.saveme
def main():
    parser = utila.cli.create_parser(
        COMMANDS,
        version=__version__,
        outputparameter=True,
        inputparameter=True,
    )
    args = utila.parse(parser)
    inputpath, output, _ = utila.sources(args)  # pylint:disable=W0612

    return utila.SUCCESS
"""

MAIN_CMD = COPYRIGHT + """\
from {%SHORT%}.cli import main

main()
"""

CODE_WORKSPACE = file_read(WORKSPACE_TEMPLATE)
GITIGNORE = file_read(join(TEMPLATES, '.gitignore'))
SETUP_PY = file_read(join(TEMPLATES, 'setup.tpy'))
SETUP_CFG = file_read(join(TEMPLATES, 'setup.cfg'))

DOC_CONF = file_read(join(TEMPLATES, 'conf.py'))

ISORT_TEMPLATE = file_read(ISORT_PATH)
CONFTEST_TEMPLATE = file_read(CONFTEST_PATH)

# None copies files
FILES = [
    # ('..code-workspace', CODE_WORKSPACE),
    (GIT_REPO_EXCLUDE, GITIGNORE),
    ('CHANGELOG.md', CHANGELOG),
    ('README.md', README),
    ('docs/bugs.rst', BUGS_RST),
    ('docs/index.rst', INDEX_RST),
    ('docs/pages/changelog.rst', CHANGELOG_RST),
    ('docs/releases/backlog.rst', BACKLOG_RST),
    ('docs/releases/releases.rst', RELEASE_RST),
    ('docs/todo.rst', TODO_RST),
    ('tests/__init__.py', COPYRIGHT),
    ('tests/conftest.py', CONFTEST_TEMPLATE),
    (REQUIREMENTS_TXT, REQUIREMENTS),
    # ('setup.py', SETUP_PY),
]


def template_replace(root: str, template: str, **kwargs):
    """Replace $vars in template

    Args:
        root(str): project root
        template(str): which contains the {%VARS%}
    Returns:
        content of template with replaced vars
    Hint:
        Vars are defined as {%VARNAME%}.
    """
    root = forward_slash(root, save_newline=False)
    short = shortcut(root)
    source = sources(root)
    name_ = name(root)
    version_tag = baw.project.version.determine(root)
    major = baw.project.version.major(version_tag)
    minor = baw.project.version.minor(version_tag)

    template = template.replace('{%SHORT%}', short)
    template = template.replace('{%SOURCES%}', ', '.join(source))
    template = template.replace('{%NAME%}', name_)
    template = template.replace('{%VERSION%}', version_tag)
    template = template.replace('{%ROOT%}', root)
    template = template.replace('{%MAJOR%}', major)
    template = template.replace('{%MINOR%}', minor)

    for key, value in kwargs.items():
        value = str(value)  # ensure to repace str
        template = template.replace('{%' + key.upper() + '%}', value)

    return template
