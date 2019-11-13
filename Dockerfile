
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
