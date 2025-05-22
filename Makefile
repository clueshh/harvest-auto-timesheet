install:
	pip install .

install-dev:
	pip install -e .[dev]

all: lint type-check test

lint:
	python3 -m ruff check .
	python3 -m ruff format --check .

format:
	python3 -m ruff check --fix .
	python3 -m ruff format .

type-check:
	python3 -m mypy

test:
	python3 -m pytest

test-htmlcov:
	python3 -m pytest --cov-report html
