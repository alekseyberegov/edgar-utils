.DEFAULT_GOAL := help

# From https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-_.]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: distro.build
distro.build:  ## Build the wheel distribution
	python setup.py bdist_wheel

.PHONY: distro.push
distro.push:  ## Push the distribution
	twine upload dist/*

.PHONY: distro.clean
distro.clean:  ## Clean distro artifacts
	rm -rf build dist edgar-utils.egg-info

.PHONY: develop.install
develop.install:  ## Install local code as the package
	pip install -e .

.PHONY: develop.setup
develop.setup:  ## Install dependencies for the development
	python setup.py develop

.PHONY: develop.test
develop.test:  ## Run tests
	pytest
