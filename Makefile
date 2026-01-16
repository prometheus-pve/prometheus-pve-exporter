# Basic make targets for building and pushing the prometheus-pve-exporter image

IMG ?= harbor.nrings.io/nrings/prometheus-pve-exporter
TAG ?= dev
PLATFORMS ?= linux/amd64,linux/arm64

.PHONY: help
help:
	@echo "Targets:"
	@echo "  docker-buildx-setup  Set up Docker buildx builder"
	@echo "  docker-build         Build the image (multi-arch)"
	@echo "  docker-push          Build and push multi-arch image to Harbor"
	@echo ""
	@echo "Variables:"
	@echo "  IMG       Image repository (default: $(IMG))"
	@echo "  TAG       Image tag (default: $(TAG))"
	@echo "  PLATFORMS Target platforms (default: $(PLATFORMS))"

.PHONY: docker-buildx-setup
docker-buildx-setup:
	@docker buildx version >/dev/null 2>&1 || (echo "Error: docker buildx not available" && exit 1)
	@if ! docker buildx inspect multiarch-builder >/dev/null 2>&1; then \
		docker buildx create --name multiarch-builder --driver docker-container --use || true; \
		docker buildx inspect --bootstrap; \
	fi

.PHONY: docker-build
docker-build: docker-buildx-setup
	@echo "Building multi-arch image for platforms: $(PLATFORMS)"
	@echo "Image: $(IMG):$(TAG)"
	@echo "Note: Multi-arch images cannot be loaded locally. Use 'docker-push' to build and push."
	docker buildx build \
		--platform $(PLATFORMS) \
		-t $(IMG):$(TAG) \
		.

.PHONY: docker-push
docker-push: docker-buildx-setup
	@echo "Building and pushing multi-arch image for platforms: $(PLATFORMS)"
	@echo "Image: $(IMG):$(TAG)"
	docker buildx build \
		--platform $(PLATFORMS) \
		-t $(IMG):$(TAG) \
		--push \
		.

