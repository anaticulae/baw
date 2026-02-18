# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

FROM alpine:3.23.3

LABEL maintainer="Helmut Konrad Schewe <helmutus@outlook.com>"

# UBUNTU
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     git \
#     python3 \
#     python3-pip \
#     python3-venv \
# && rm -rf /var/lib/apt/lists/*

# ALPINE
RUN apk add --no-cache \
    git \
    python3 \
    py3-pip \
    python3-dev

ENV BAW_VENV_GLOBAL=0
ENV BAW_VENV_ALWAYS=0

ENV BAW=/tmp/dev

ENV PYLINTHOME=/tmp/pylint

ENV SHARED_SPACE=/tmp/shared
ENV SHARED_TMP=/tmp/shared/tmp
ENV SHARED_TODO=/tmp/shared/todo
ENV SHARED_READY=/tmp/shared/ready

ENV GIT_AUTHOR_NAME='Automated Release'
ENV GIT_AUTHOR_EMAIL='automated_release@ostia.la'

ENV CAELUM_DOCKER_TEST='localhost'
ENV CAELUM_DOCKER_RUNTIME='localhost'

COPY /baw/templates/.gitignore /var/install/.gitignore
RUN git config --global --add core.excludesFile /var/install/.gitignore

# Create venv
RUN python3 -m venv /opt/venv
# Use venv's pip explicitly
ENV PATH="/opt/venv/bin:$PATH"

# TODO: INVESTIGATE THIS HACK
RUN mkdir -m 777 /.local /.cache /.pylint.d && chmod -R 777 /tmp

COPY /requirements.txt\
     /baw/sync/dev\
     /baw/sync/doc\
        /var/install/

WORKDIR /var/install

RUN pip install --upgrade pip &&\
    pip install -r requirements.txt &&\
    pip install -r dev &&\
    pip install -r doc

COPY . /var/install

RUN pip install --no-deps . && baw --help

WORKDIR /var/outdir
WORKDIR /var/workdir

ENTRYPOINT ["sh", "-c"]
