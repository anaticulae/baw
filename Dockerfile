# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

FROM 169.254.149.20:6001/arch_python_git:v0.17.5

MAINTAINER HELMUT KONRAD SCHEWE

ENV BAW_VENV_GLOBAL=0
ENV BAW_VENV_ALWAYS=0

ENV BAW=/tmp/dev

ENV PYLINTHOME=/tmp/pylint

ENV SHARED_SPACE=/tmp/shared
ENV SHARED_TMP=/tmp/shared/tmp
ENV SHARED_TODO=/tmp/shared/todo
ENV SHARED_READY=/tmp/shared/ready

ENV GITEA_SERVER_URL='169.254.149.20:6300'
ENV GITEA_TOKEN='SECRET'
ENV GIT_AUTHOR_NAME='Automated Release'
ENV GIT_AUTHOR_EMAIL='automated_release@ostia.la'

ENV CAELUM_DOCKER_TEST='169.254.149.20:6001'
ENV CAELUM_DOCKER_RUNTIME='169.254.149.20:2375'

COPY /baw/templates/.gitignore /var/install/.gitignore
RUN git config --global --add core.excludesFile /var/install/.gitignore

RUN /usr/sbin/python -m pip install --upgrade pip

COPY /requirements.txt\
     /baw/sync/dev\
     /baw/sync/doc\
        /var/install/

WORKDIR /var/install

RUN python -mpip install -r requirements.txt &&\
    python -mpip install -r dev &&\
    python -mpip install -r doc

COPY . /var/install

RUN python -mpip install .

# TODO: INVESTIGATE THIS HACK
RUN mkdir -m 777 /.local /.cache /.pylint.d
RUN chmod -R 777 /tmp

WORKDIR /var/outdir
WORKDIR /var/workdir

ENTRYPOINT ["sh", "-c"]
