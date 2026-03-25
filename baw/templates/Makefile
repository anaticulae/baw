
.PHONY: docker-build docker-run build clean

VERSION := $(shell git rev-parse --short HEAD 2>/dev/null || echo "latest")
CURDIR := $(CURDIR)

NAME = {{PACKAGE}}
IMAGE := $(NAME):$(VERSION)
IMAGE_BASE_NAME := ghcr.io/anaticulae/{{PACKAGE}}:$(VERSION)
IMAGE_TEST_NAME := ghcr.io/anaticulae/{{PACKAGE}}:$(VERSION)-test

docker-build:
	docker build -t $(IMAGE) .

# --progress=plain
docker-build-test:
	docker build -f env/test/Dockerfile -t $(IMAGE_TEST_NAME) .

docker-build-base:
	docker build -f env/base/Dockerfile -t $(IMAGE_BASE_NAME) .

docker-upload-test:
	docker push $(IMAGE_TEST_NAME)

docker-upload-base:
	docker push $(IMAGE_BASE_NAME)

docker-doctest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw test docs"

docker-fasttest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw test fast"

docker-longtest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw test long"

docker-alltest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw test all -n1"

docker-lint: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE) "baw lint all"

docker-release: docker-build
	docker run -v $(CURDIR):/var/workdir\
			-e GH_TOKEN=$(GH_TOKEN) $(IMAGE)\
			"baw release --no_test --no_linter"
