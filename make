#!/usr/bin/bash
# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

REPO="169.254.149.20:6001"
NAME="arch_python_git_baw"
VERSION="$(git describe)"
TAG="${REPO}/${NAME}:${VERSION}"

docker build -t $TAG .

if [ $? -ne 0 ]
then
    echo "could not run docker build: ${file}"
    exit 1
fi
