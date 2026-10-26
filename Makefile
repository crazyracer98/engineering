# The release contract release.yml drives -- see docs/TEMPLATE.md's
# "Release: a Makefile contract" section. This template itself ships no
# artifact, so every target is a documented no-op; an instance reimplements
# each target for its own artifact type (an OCI image, a package, a chart,
# ...) without needing to touch release.yml.

.PHONY: release-arches build sbom release-assets publish publish-packages verify-published release-check finalize

# `uv` comes from PATH when present (devcontainer, local, pages.yml). On a bare
# runner (release.yml's build job) the pinned release from .devcontainer/Dockerfile
# (Renovate's single source of truth) is installed under build/ (gitignored).
UV_VERSION := $(shell sed -n 's/^ARG UV_VERSION=//p' .devcontainer/Dockerfile | head -n1)
UV_DIR := build/.tools/uv
ifeq ($(shell command -v uv 2>/dev/null),)
UV := $(UV_DIR)/uv
UV_DEP := $(UV)
else
UV := uv
UV_DEP :=
endif

$(UV_DIR)/uv:
	@test -n "$(UV_VERSION)" || { echo "error: no ARG UV_VERSION= in .devcontainer/Dockerfile" >&2; exit 1; }
	curl -LsSf --retry 3 https://astral.sh/uv/$(UV_VERSION)/install.sh | env UV_INSTALL_DIR=$(UV_DIR) UV_NO_MODIFY_PATH=1 sh

# Prints (only) a JSON array of the arches to build on, once, first. Each
# arch then runs build/sbom/release-assets/publish natively on its own runner.
release-arches:
	@echo '["amd64"]'

# publication/ (Markdown + YAML), the site (build/site) and the PDF paper
# (build/paper.pdf, build/references.json). Pandoc and Typst come from PyPI,
# so only `uv` is needed (bootstrapped above when missing).
build: $(UV_DEP)
	$(UV) run --locked taxonomy build
	NO_MKDOCS_2_WARNING=1 $(UV) run --locked taxonomy site --out build/site
	$(UV) run --locked taxonomy paper --out build/paper.pdf

sbom:
	@echo "template-base ships no artifact -- nothing to scan."

# Run after `build` (release.yml does); the names are linked from the site and README: keep them.
release-assets:
	@mkdir -p dist
	cp build/paper.pdf dist/engineering-best-practices.pdf
	cp publication/engineering-best-practices.md dist/engineering-best-practices.md
	cp publication/engineering-best-practices.yaml dist/engineering-best-practices.yaml
	cp build/references.json dist/references.json

# Per arch: image registries only (a package must not be published here --
# it would run once per arch; use publish-packages).
publish:
	@echo "template-base ships no artifact -- nothing to publish."

# Once, after every arch leg, and only when the instance sets PYPI_PUBLISH,
# NPM_PUBLISH or CARGO_PUBLISH: PyPI / npm / crates.io. dist/ holds every
# arch leg's files.
# This default must not silently skip a configured publish: an instance that
# sets a *_PUBLISH variable but still uploads from `publish` would otherwise
# release without its package.
publish-packages:
	@set -e; \
	for v in PYPI_PUBLISH NPM_PUBLISH CARGO_PUBLISH; do \
	  if [ -n "$$(printenv $$v)" ]; then \
	    echo "error: this instance sets $$v but its Makefile doesn't implement publish-packages; move the package upload from publish into publish-packages (see docs/TEMPLATE.md)" >&2; \
	    exit 1; \
	  fi; \
	done; \
	echo "template-base ships no package -- nothing to publish."

# Once, after publish-packages succeeded, and only when the instance sets
# PYPI_PUBLISH, NPM_PUBLISH or CARGO_PUBLISH: check the published release
# from the registry (e.g. install it). A no-op here on purpose: there is
# nothing to verify unless an instance implements it.
verify-published:
	@echo "template-base ships no package -- nothing to verify."

# Runs once after every arch leg, inside the devcontainer with the stack up.
release-check:
	@echo "template-base ships no artifact -- nothing to check."

# Runs once after release-check, on the host runner (e.g. combine per-arch
# registry tags into a multi-arch manifest list).
finalize:
	@echo "template-base ships no artifact -- nothing to finalize."
