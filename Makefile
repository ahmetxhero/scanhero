.PHONY: help install install-dev test test-cov lint format clean build publish

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=scanhero --cov-report=html --cov-report=term-missing

lint: ## Run linting
	flake8 src/ tests/
	mypy src/

format: ## Format code
	black src/ tests/ examples/
	isort src/ tests/ examples/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python -m build

publish-test: ## Publish to TestPyPI
	python -m build
	python -m twine upload --repository testpypi dist/*

publish: ## Publish to PyPI
	python -m build
	python -m twine upload dist/*

pre-commit: ## Install pre-commit hooks
	pre-commit install

pre-commit-run: ## Run pre-commit hooks on all files
	pre-commit run --all-files

test-install: ## Test installation and basic functionality
	python test_installation.py

example-basic: ## Run basic usage example
	python examples/basic_usage.py

example-advanced: ## Run advanced usage example
	python examples/advanced_usage.py

cli-test: ## Test CLI functionality
	scanhero scan 127.0.0.1 --ports 80,443,22 --format console
	scanhero scan 127.0.0.1 --ports 80,443,22 --format json
	scanhero scan 127.0.0.1 --ports 80,443,22 --format csv

check: ## Run all checks (lint, format, test)
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) test

all: ## Run all checks and build
	$(MAKE) clean
	$(MAKE) install-dev
	$(MAKE) check
	$(MAKE) build
