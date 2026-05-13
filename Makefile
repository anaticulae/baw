.PHONY: docker-build docker-run build clean

VERSION := $(shell git rev-parse --short HEAD 2>/dev/null || echo "latest")
CURDIR := $(CURDIR)

NAME = baw
IMAGE := $(NAME):$(VERSION)
IMAGE_BASE_NAME := ghcr.io/anaticulae/$(IMAGE)
IMAGE_TEST_NAME := ghcr.io/anaticulae/$(IMAGE)-test
IMAGE_PYTH_NAME := ghcr.io/anaticulae/$(IMAGE)-python

docker-build:
	docker build -t $(IMAGE) .

# --progress=plain
docker-build-test:
	docker build -f env/test/Dockerfile -t $(IMAGE_TEST_NAME) .

docker-build-base:
	docker build -f env/base/Dockerfile -t $(IMAGE_BASE_NAME) .

docker-build-python:
	docker build -f env/python/Dockerfile -t $(IMAGE_PYTH_NAME) .

docker-upload-test:
	docker push $(IMAGE_TEST_NAME)

docker-upload-base:
	docker push $(IMAGE_BASE_NAME)

docker-upload-python:
	docker push $(IMAGE_PYTH_NAME)

docker-doctest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw test docs"

docker-fasttest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw test fast"

docker-longtest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw test long"

docker-alltest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw test all"

docker-lint: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw lint all"

docker-release: docker-build
	@if git describe --exact-match --tags HEAD >/dev/null 2>&1; then \
		echo "Current commit is already tagged, skipping release."; \
	else \
		docker run \
			-v $(CURDIR):/var/workdir\
			-e GH_TOKEN=$(GH_TOKEN) $(IMAGE)\
			"baw release --no_test --no_linter"; \
	fi
