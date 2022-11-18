# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import baw.cmd.image
import baw.dockers
import baw.utils


def images() -> int:
    with baw.dockers.client() as client:
        for image in client.images.list():
            if baw.cmd.image.TEST_TAG not in str(image):
                continue
            baw.utils.log(f'remove: {image.id}')
            image.remove(force=True)
    return baw.utils.SUCCESS
