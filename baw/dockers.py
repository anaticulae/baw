# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import sys

import baw.config
import baw.run
import baw.utils


def switch_docker():
    """Use docker environment to run command."""
    usedocker = '--docker' in sys.argv
    if not usedocker:
        return baw.run.run_main()
    root = os.getcwd()
    # use docker to run cmd
    argv = [item for item in sys.argv if item != '--docker']
    if argv:
        # TODO: REMOVE THIS HACK
        argv[0] = argv[0].split('/')[-1]
    usercmd = ' '.join(argv)
    image = baw.config.docker_image(root=root)
    # TODO: MOVE TO CONFIG OR SOMETHING ELSE
    volume = f'-v {os.getcwd()}:/var/test'
    docker = f'docker run --rm {volume} {image} "{usercmd}"'
    completed = baw.runtime.run(docker, cwd=root)
    if completed.returncode:
        baw.utils.error(docker)
        if completed.stdout:
            baw.utils.error(completed.stdout)
        baw.utils.error(completed.stderr)
    else:
        baw.utils.log(completed.stdout)
        if completed.stderr:
            baw.utils.error(completed.stderr)
    return completed.returncode
