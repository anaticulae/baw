# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

FROM 169.254.149.20:6001/arch_python_git:0.15.1

MAINTAINER HELMUT KONRAD FAHRENDHOLZ

ENV BAW_VENV_GLOBAL=1
ENV BAW_VENV_ALWAYS=1

ENV BAW=/tmp/dev

ENV PYLINTHOME=/tmp/pylint

ENV SHARED_SPACE=/tmp/shared
ENV SHARED_TMP=/tmp/shared/tmp
ENV SHARED_TODO=/tmp/shared/todo
ENV SHARED_READY=/tmp/shared/ready

ENV GITEA_SERVER_URL='169.254.149.20:6300'
ENV GIT_AUTHOR_NAME='Automated Release'
ENV GIT_AUTHOR_EMAIL='automated_release@ostia.la'

ENV CAELUM_DOCKER_TEST='169.254.149.20:6001'
ENV CAELUM_DOCKER_RUNTIME='169.254.149.20:2375'

RUN /usr/sbin/python -m pip install --upgrade pip

COPY /requirements.txt\
     /baw/requires/requirements-dev.txt\
     /baw/requires/requirements-doc.txt\
        /var/install/

WORKDIR /var/install

RUN python -mpip install -r requirements.txt &&\
    python -mpip install -r requirements-dev.txt &&\
    python -mpip install -r requirements-doc.txt

COPY . /var/install

RUN python -mpip install .

# TODO: INVESTIGATE THIS HACK
RUN mkdir -m 777 /.local /.cache /.pylint.d
RUN chmod -R 777 /tmp

WORKDIR /var/workdir

ENTRYPOINT ["sh", "-c"]
