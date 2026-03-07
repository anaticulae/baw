.PHONY: docker-build docker-run build clean

VERSION := $(shell git rev-parse --short HEAD 2>/dev/null || echo "latest")
CURDIR := $(CURDIR)

NAME = baw
IMAGE := $(NAME):$(VERSION)
IMAGE_TEST_NAME := ghcr.io/anaticulae/baw:$(VERSION)-test

docker-build:
	docker build -t $(IMAGE) .

# --progress=plain
docker-build-test:
	docker build -f env/test -t $(IMAGE_TEST_NAME) .

docker-upload-test:
	docker push $(IMAGE_TEST_NAME)

docker-doctest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw test docs"

docker-fasttest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw test fast"

docker-longtest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw test long"

docker-alltest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw test all -n16"

docker-lint: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw lint all"
