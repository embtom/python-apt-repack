ROOT := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: prepare package package-arm64 build-deb build-deb-arm64 \
        develop develop-arm64 lint lint-arm64 test test-arm64 clean clean-arm64 \
        builder builder-arm64

# -------------------------------------------------------------------
# Inside container: real build logic
# -------------------------------------------------------------------
ifeq ($(INSIDE_CONTAINER),1)

all: develop lint test package

package:
	@echo "==> Creating wheel and sdist package (ARCH=$(ARCH))"
	python3 -m build -w --config-setting=build-dir="build/$(ARCH)"

develop:
	@echo "==> Installing development dependencies (ARCH=$(ARCH))"
	python3 -m pip install --editable .[dev] --verbose \
		--config-setting=build-dir="build/$(ARCH)"

lint:
	@echo "==> Running linters"
	@$(ROOT)/pre-build.sh

test:
	@echo "==> Running tests"all: develop lint test package
	@$(ROOT)/utils/test_runner.py

clean:
	@echo "==> Cleaning build artifacts"
	rm -rf build dist *.egg-info .pytest_cache
	find . -name "__pycache__" -exec rm -rf {} +

build-deb:
	@echo "==> Building Debian package"
	mkdir -p build/work
	rsync -a \
  		--exclude=.git \
  		--exclude=.devcontainer \
  		--exclude=build \
  		./ /src/build/work/
	cd build/work && dpkg-buildpackage \
		--unsigned-source \
		--unsigned-changes \
		--post-clean \
		--build=binary 
	rm -rf build/work

else

# -------------------------------------------------------------------
# Outside container: native builder targets
# -------------------------------------------------------------------
all-arm64 package-arm64 develop-arm64 lint-arm64 test-arm64 clean-arm64 build-deb-arm64:
	@BASE=$(@:%-arm64=%) ; \
	echo ">>> Running inside ARM64 builder: $$BASE" ; \
	podman-compose -f docker-compose.yml run --rm builder-arm64 $$BASE

all package develop lint test clean build-deb:
	@echo ">>> Running inside native builder: $@" ; \
	podman-compose -f docker-compose.yml run --rm builder $@

builder:
	podman-compose -f docker-compose.yml build builder

builder-arm64:
	podman-compose -f docker-compose.yml build builder-arm64

endif
