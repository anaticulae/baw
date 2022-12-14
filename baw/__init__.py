#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

ROOT = None

__version__ = '1.35.1'

# pylint:disable=wrong-import-position
import baw.__patch__
import baw.__root__
from baw.dockers.dockfile import docker_image_upgrade
from baw.pipelinefile import jenkinsfile
