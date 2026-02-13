.PHONY: docker-build docker-run build clean

VERSION := $(shell git rev-parse --short HEAD 2>/dev/null || echo "latest")
CURDIR := $(CURDIR)

NAME = baw
IMAGE := $(NAME):$(VERSION)


docker-build:
	docker build -t $(IMAGE) .

docker-doctest: docker-build
	docker run -i -v $(CURDIR):/var/workdir $(IMAGE) "baw test docs"

docker-fasttest: docker-build
	docker run -i -v $(CURDIR):/var/workdir $(IMAGE) "baw test fast"
