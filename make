#!/usr/bin/bash
# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

REPO="169.254.149.20:6001"
CURRENT=$(baw info describe)

build(){
    file=$1   # Python
    from=$2   # arch_python_git
    tag=$3    # arch_python_git_baw

    echo ""
    echo "build: $tag"

    TAG="${CAELUM_DOCKER_TEST}/$tag:${CURRENT}"
    sed -i "s/arch_python_git/${from}/" $file >> $file
    baw image create --name $TAG --dockerfile $file
    git checkout $1

    if [ $? -ne 0 ]
    then
        echo "could not run docker build: ${file}"
        exit 1
    fi

    # verify that image is created properly
    baw image run --name "${TAG}" --cmd "ls /var/install"

    if [ $? -ne 0 ]
    then
        echo "could verify docker build: ${TAG}"
        exit 1
    fi
}

build Dockerfile    arch_python_git                 arch_python_git_baw
build Dockerfile    arch_python_git_ghost           arch_python_git_ghost_baw
build Dockerfile    arch_python_git_ghost_opencv    arch_python_git_ghost_opencv_baw

# build git runner
pushd env && ./make; popd
