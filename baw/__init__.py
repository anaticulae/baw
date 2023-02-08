#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

ROOT = None

__version__ = '1.66.0'

# pylint:disable=wrong-import-position
import baw.__patch__
import baw.__root__
from baw.config import shortcut
from baw.dockers.dockfile import docker_image_upgrade
from baw.git import add as git_add
from baw.git import checkout as git_checkout
from baw.git import commit as git_commit
from baw.git import is_clean as git_isclean
from baw.git import push as git_push
from baw.git import reset as git_reset
from baw.git import stash as git_stash
from baw.pipelinefile import jenkinsfile
from baw.project import determine_root
from baw.runtime import hasprog
from baw.utils import FAILURE
from baw.utils import SUCCESS
from baw.utils import completed
from baw.utils import error
from baw.utils import exitx
from baw.utils import file_append
from baw.utils import file_create
from baw.utils import log
from baw.utils import tmpname
