
.PHONY: docker-build docker-run build clean

VERSION := $(shell git rev-parse --short HEAD 2>/dev/null || echo "latest")
CURDIR := $(CURDIR)

NAME = {{PACKAGE}}
IMAGE := $(NAME):$(VERSION)
IMAGE_NAME := ghcr.io/anaticulae/$(IMAGE)

docker-build:
	docker build -t $(IMAGE_NAME) .

docker-upload:
	docker push $(IMAGE_NAME)

docker-doctest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE_NAME) "baw test docs"

docker-fasttest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE_NAME) "baw test fast"

docker-longtest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE_NAME) "baw test long"

docker-alltest: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE_NAME) "baw test all"

docker-lint: docker-build
	docker run -v $(CURDIR):/var/workdir $(IMAGE_NAME) "baw lint all"

docker-release: docker-build
	docker run -v $(CURDIR):/var/workdir\
			-e GH_TOKEN=$(GH_TOKEN) $(IMAGE_NAME)\
			"baw release --no_test --no_linter"
