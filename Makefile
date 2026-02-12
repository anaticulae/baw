.PHONY: docker-build docker-run build clean

VERSION := $(shell git rev-parse --short HEAD 2>/dev/null || echo "latest")

IMAGE_NAME = baw
CONTAINER_NAME = builder


docker-build:
	docker build -t $(IMAGE_NAME):$(VERSION) .

docker-run: docker-build
	docker run -i $(IMAGE_NAME) "baw test docs"
