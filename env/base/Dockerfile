# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

FROM alpine:3.23.4

LABEL maintainer="Helmut Konrad Schewe <helmutus@outlook.com>"

# ALPINE
RUN apk add --no-cache \
    git \
    python3 \
    py3-pip \
    python3-dev

ENV PYLINTHOME=/tmp/pylint

COPY ../baw/templates/.gitignore /var/install/.gitignore
RUN git config --global --add core.excludesFile /var/install/.gitignore &&\
    git config --global --add safe.directory /var/workdir

# Create venv
RUN python3 -m venv /opt/venv && source /opt/venv/bin/activate
# Use venv's pip explicitly
ENV PATH="/opt/venv/bin:$PATH"

# TODO: INVESTIGATE THIS HACK
RUN mkdir -m 777 /.local /.cache /.pylint.d && chmod -R 777 /tmp

# cache requirements
WORKDIR /var/install
COPY ../../pyproject.toml /var/install
RUN python -m pip install --upgrade pip setuptools wheel &&\
    pip install .

# install baw as base application
COPY ../.. /var/install

RUN pip install . &&\
    baw --help

# remove baw app source code
RUN rm -rf /var/install

WORKDIR /var/workdir

ENTRYPOINT ["sh"]
