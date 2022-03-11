# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from baw:0.0.1

# run apt-get update && \
#     apt-get install -y xorg xvfb libxss-dev libgtk2.0-0 gconf2 libnss3 libasound2

# env cxx="g++-4.9"
# env cc="gcc-4.9"
# env display=:99.0

workdir /application
copy tests ./tests
copy baw ./baw

# ENTRYPOINT ["sh", "-c", "(Xvfb $DISPLAY -screen 0 1024x768x16 &) && npm run test"]
