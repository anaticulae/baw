#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

ROOT = None

__version__ = '1.70.2'

# pylint:disable=wrong-import-position
import baw.__root__
from baw.gix import git_add
from baw.gix import git_commit
from baw.gix import git_stash
from baw.gix import is_clean
from baw.project import determine_root
from baw.runtime import hasprog
from baw.utils import FAILURE
from baw.utils import NEWLINE
from baw.utils import SUCCESS
from baw.utils import completed
from baw.utils import debug
from baw.utils import error
from baw.utils import exitx
from baw.utils import file_create
from baw.utils import file_replace
from baw.utils import forward_slash
from baw.utils import log
from baw.utils import skip
from baw.utils import tmpname
