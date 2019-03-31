extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.githubpages',
    'sphinx.ext.imgmath',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',

    # Used to write beautiful docstrings:
    'sphinx.ext.napoleon',
    # Used to include .md files:
    'm2r',
    # Used to insert typehints into the final docs:
    'sphinx_autodoc_typehints',
    # Used to embed values from the source code into the docs:
    'added_value',
    # Used to build graphs:
    'sphinxcontrib.mermaid',
]

source_suffix = ['.rst']

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = '$_NAME_$'
copyright = '2019, kiwi project'
author = 'Helmut Konrad Fahrendholz'

version = '$_VERSION_$'
release = '$_VERSION_$'

language = "en"
pygments_style = 'sphinx'

todo_include_todos = True

html_theme = 'default'

htmlhelp_basename = '$_SHORT_$'

# Napoleon settings
napoleon_google_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_ivar = True
napoleon_use_rtype = True
napoleon_use_keyword = True
