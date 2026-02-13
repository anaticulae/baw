.PHONY: docker-build docker-run build clean

VERSION := $(shell git rev-parse --short HEAD 2>/dev/null || echo "latest")
CURDIR := $(CURDIR)

IMAGE_NAME = baw
CONTAINER_NAME = builder


docker-build:
	docker build -t $(IMAGE_NAME):$(VERSION) .

docker-doctest: docker-build
	docker run -i -v $(CURDIR):/var/workdir $(IMAGE_NAME) "baw test docs"

docker-fasttest: docker-build
	docker run -i -v $(CURDIR):/var/workdir $(IMAGE_NAME) "baw test fast"
