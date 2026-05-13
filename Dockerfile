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

ENV BAW=/tmp/dev

ENV PYLINTHOME=/tmp/pylint

COPY /baw/templates/.gitignore /var/install/.gitignore
RUN git config --global --add core.excludesFile /var/install/.gitignore &&\
    git config --global --add safe.directory /var/workdir

# Create venv.
RUN python -m venv /opt/venv
# Use venv's pip explicitly
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip

WORKDIR /var/install

COPY pyproject.toml .

RUN pip install .[dev,doc]
RUN pip install .

COPY . /var/install

RUN pip install . && baw --help

WORKDIR /var/outdir
WORKDIR /var/workdir

ENTRYPOINT ["sh", "-c"]
