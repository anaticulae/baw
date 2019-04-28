"""Base for generating project. Templates have to be here."""
from os.path import exists
from os.path import join

from baw.config import name
from baw.config import shortcut
from baw.git import GIT_REPO_EXCLUDE
from baw.project import version
from baw.utils import BAW_EXT
from baw.utils import REQUIREMENTS_TXT
from baw.utils import ROOT
from baw.utils import file_read

FOLDERS = [
    BAW_EXT,
    'tests',
    'docs',
]

TEMPLATES = join(ROOT, 'templates')
assert exists(TEMPLATES), 'No template-dir %s' % TEMPLATES

WORKSPACE_TEMPLATE = join(TEMPLATES, '..code-workspace')
assert exists(WORKSPACE_TEMPLATE), 'No template %s' % WORKSPACE_TEMPLATE

GIT_IGNORE_TEMPLATE = join(TEMPLATES, '.gitignore')
assert exists(GIT_IGNORE_TEMPLATE), 'No gitignore %s' % GIT_IGNORE_TEMPLATE

README = """# $_SHORT_$
"""

CHANGELOG = """# Changelog

Every noteable change is logged here.
"""

LICENCE = """# Licence
"""

TODO = """# Todo
"""

BUGS = """# Bugs

## open

## closed
"""

BUGS_RST = """.. mdinclude:: ../../BUGS.md
"""
CHANGELOG_RST = """.. mdinclude:: ../../CHANGELOG.md
"""
TODO_RST = """.. mdinclude:: ../../TODO.md
"""
README_RST = """.. mdinclude:: ../../README.md
"""

INDEX_RST = """Welcome to $_NAME_$
=================================

.. toctree::
  :maxdepth: 1

  pages/readme

  pages/changelog

  pages/bugs

  pages/todo

Modules
--------------------
.. toctree::
   :maxdepth: 5

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
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
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
            'console_scripts': ['$_SHORT_$ = $_SHORT_$.command:main'],
        },
"""

INIT_CMD = COPYRIGHT + """\
from utila import SUCCESS
from utila import create_parser
from utila import parse
from utila import saveme
from utila import sources

from $_SHORT_$ import __version__

COMMANDS = [] # add additonal commands here

@saveme
def main():
    parser = create_parser(
        COMMANDS,
        version=__version__,
        outputparameter=True,
        inputparameter=True,
    )
    args = parse(parser)
    inputpath, output = sources(args)

    return SUCCESS
"""

MAIN_CMD = COPYRIGHT + """\
from $_SHORT_$.command import main

main()
"""

CODE_WORKSPACE = file_read(WORKSPACE_TEMPLATE)
GITIGNORE = file_read(join(TEMPLATES, '.gitignore'))

SETUP_PY = file_read(join(TEMPLATES, 'setup.py'))
SETUP_CFG = file_read(join(TEMPLATES, 'setup.cfg'))

DOC_CONF = file_read(join(TEMPLATES, 'conf.py'))

# None copies files
FILES = [
    ('..code-workspace', CODE_WORKSPACE),
    (GIT_REPO_EXCLUDE, GITIGNORE),
    ('BUGS.md', BUGS),
    ('CHANGELOG.md', CHANGELOG),
    ('LICENCE.md', LICENCE),
    ('README.md', README),
    ('TODO.md', TODO),
    ('docs/index.rst', INDEX_RST),
    ('docs/pages/bugs.rst', BUGS_RST),
    ('docs/pages/changelog.rst', CHANGELOG_RST),
    ('docs/pages/readme.rst', README_RST),
    ('docs/pages/todo.rst', TODO_RST),
    (REQUIREMENTS_TXT, REQUIREMENTS),
    # ('setup.py', SETUP_PY),
]


def template_replace(root: str, template: str):
    """Replace $vars in template

    Args:
        root(str): project root
        template(str): which contains the $_VARS_$
    Returns:
        content of template with replaced vars
    Hint:
        Vars are defined as $_VARNAME_$.
    """
    short = shortcut(root)
    name_ = name(root)
    version_tag = version(root)

    template = template.replace('$_SHORT_$', short)
    template = template.replace('$_NAME_$', name_)
    template = template.replace('$_VERSION_$', version_tag)
    template = template.replace('$_ROOT_$', root)

    return template
