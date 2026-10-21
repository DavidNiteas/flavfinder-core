.PHONY: install install-autogluon test lint build clean

install:
	python -m pip install -e ".[dev]"

install-autogluon:
	python -m pip install -e ".[dev,autogluon]"

test:
	python -m pytest

lint:
	ruff check .
	mypy src/flavfinder

build:
	python -m build

clean:
	rm -rf build dist .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
