import sys

# put to the start to avoid overwriting by other modules/packages.
sys.path.insert(0, r'{{ROOT}}/tests')
sys.path.insert(0, r'{{ROOT}}')

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',

    # Used to write beautiful docstrings:
    'sphinx.ext.napoleon',
    # Used to include .md files:
    'recommonmark',
    # Used to insert typehints into the final docs:
    'sphinx_autodoc_typehints',
    # Used to embed values from the source code into the docs:
    'added_value',
]

source_suffix = ['.rst']

source_parsers = {
    '.md': 'recommonmark.parser.CommonMarkParser',
}

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = '{{NAME}}'
copyright = '2019-{{YEAR}}, kiwi project'
author = 'Helmut Konrad Fahrendholz'

version = '{{VERSION}}'
release = '{{VERSION}}'

language = "en"
pygments_style = 'sphinx'

html_theme = 'default'

htmlhelp_basename = '{{SHORT}}'

# Napoleon settings
napoleon_google_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_ivar = True
napoleon_use_rtype = True
napoleon_use_keyword = True
