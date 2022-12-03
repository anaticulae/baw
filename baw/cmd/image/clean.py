# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import docker.errors

import baw.cmd.image
import baw.dockers
import baw.utils


def images() -> int:
    with baw.dockers.client() as client:
        for image in client.images.list():
            imagename = str(image)
            delete = baw.cmd.image.TEST_TAG in imagename
            if not delete:
                continue
            baw.utils.log(f'try to remove: {image.id}')
            try:
                image.remove(force=True)
            except docker.errors.APIError:
                baw.utils.error(f'could not remove {image.id}')
    return baw.utils.SUCCESS
