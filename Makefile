.PHONY: docker-build docker-run build clean

VERSION := $(shell git rev-parse --short HEAD 2>/dev/null || echo "latest")
TAG := $(shell git describe --tags --always 2>/dev/null || echo "latest")
CURDIR := $(CURDIR)

NAME = baw
IMAGE := $(NAME):$(VERSION)
IMAGE_BASE := ghcr.io/anaticulae/$(IMAGE)
IMAGE_TEST_NAME := ghcr.io/anaticulae/$(IMAGE)-test
IMAGE_PYTH_NAME := ghcr.io/anaticulae/$(IMAGE)-python

docker-build:
	docker build -t $(IMAGE_BASE) .

docker-build-test:
	docker build -f env/test/Dockerfile -t $(IMAGE_TEST_NAME) .

docker-build-base:
	docker build -f env/base/Dockerfile -t $(IMAGE_BASE) .

docker-build-python:
	docker build -f env/python/Dockerfile -t $(IMAGE_PYTH_NAME) .

docker-upload-test:
	docker push $(IMAGE_TEST_NAME)
	docker tag $(IMAGE_TEST_NAME) $(subst :$(VERSION),:$(TAG),$(IMAGE_TEST_NAME))
	docker push $(subst :$(VERSION),:$(TAG),$(IMAGE_TEST_NAME))

docker-upload-base:
	docker push $(IMAGE_BASE)
	docker tag $(IMAGE_BASE) $(subst :$(VERSION),:$(TAG),$(IMAGE_BASE))
	docker push $(subst :$(VERSION),:$(TAG),$(IMAGE_BASE))

docker-upload-python:
	docker push $(IMAGE_PYTH_NAME)
	docker tag $(IMAGE_PYTH_NAME) $(subst :$(VERSION),:$(TAG),$(IMAGE_PYTH_NAME))
	docker push $(subst :$(VERSION),:$(TAG),$(IMAGE_PYTH_NAME))

docker-doctest: docker-build
	docker run \
		-v $(CURDIR):/var/workdir \
		$(IMAGE_BASE) \
		"baw test docs"

docker-fasttest: docker-build
	docker run \
		-v $(CURDIR):/var/workdir \
		$(IMAGE_BASE) \
		"baw test fast"

docker-longtest: docker-build
	docker run \
		-v $(CURDIR):/var/workdir \
		$(IMAGE_BASE) \
		"baw test long"

docker-alltest: docker-build
	docker run \
		-v $(CURDIR):/var/workdir \
		$(IMAGE_BASE) \
		"baw test all"

docker-lint: docker-build
	docker run \
		-v $(CURDIR):/var/workdir \
		$(IMAGE_BASE) \
		"baw lint all"

docker-release: docker-build
	@if git describe --exact-match --tags HEAD >/dev/null 2>&1; then \
		echo "Current commit is already tagged, skipping release."; \
	else \
		docker run \
			-v $(CURDIR):/var/workdir\
			-e GH_TOKEN\
			$(IMAGE_BASE)\
			"baw release --no_test --no_linter"; \
	fi
