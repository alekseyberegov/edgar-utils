.DEFAULT_GOAL := help

DOC_INDEX := file://$(abspath $(dir $(lastword $(MAKEFILE_LIST)))/docs/_build/html/index.html)

# From https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-_.]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: dist.build
dist.build:  ## Build the wheel distribution
	python3 setup.py bdist_wheel

.PHONY: dist.push
dist.push:  ## Push the distribution
	twine upload dist/*

.PHONY: dist.clean
dist.clean:  ## Clean distro artifacts
	rm -rf build dist edgar-utils.egg-info

.PHONY: dev.install
dev.install:  ## Install local code as the package
	pip install -e .

.PHONY: dev.setup
dev.setup:  ## Install dependencies for the development
	python setup.py develop

.PHONY: dev.test
dev.test:  ## Run tests
	pytest --cov=edgar

doc.html:  ## Generate HTML documentation
	cd docs && $(MAKE) html

doc.clean:  ## Clean HTML documentation
	cd docs && $(MAKE) clean

doc.open:  ## Open the documentation in the default browser
	python -m webbrowser $(DOC_INDEX)