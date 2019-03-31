"""Base for generating project. Templates have to be here."""
from collections import namedtuple
from os.path import exists
from os.path import join

from baw import __version__
from baw import ROOT
from baw.config import name
from baw.config import shortcut
from baw.utils import BAW_EXT
from baw.utils import file_read
from baw.utils import GIT_REPO_EXCLUDE

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

README = """# $_SHORT_$ - $_NAME_$
"""

CHANGELOG = """# Changelog

Every noteable change is logged here.
"""

LICENCE = """# Licence
"""

TODO = """# TODO
"""

BUGS = """# BUGS
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

   tmp/modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""

REQUIREMENTS = ""

INIT = """from os.path import abspath
from os.path import dirname
from os.path import join

__version__ = '0.0.0'

THIS = dirname(__file__)
ROOT = abspath(join(THIS, '..'))
"""

CODE_WORKSPACE = file_read(WORKSPACE_TEMPLATE)
GITIGNORE = file_read(join(TEMPLATES, '.gitignore'))
SETUP = file_read(join(TEMPLATES, 'setup.cfg'))

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
    ('requirements.txt', REQUIREMENTS),
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

    template = template.replace('$_SHORT_$', short)
    template = template.replace('$_NAME_$', name_)
    template = template.replace('$_VERSION_$', __version__)

    return template
