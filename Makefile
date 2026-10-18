.PHONY: all build test lint format clean run

all: build

build:
	python3 -m pip install -e . --no-deps

test:
	pytest -v tests/

lint:
	ruff check .
	mypy --strict src/

format:
	ruff format --check .

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache dist build src/*.egg-info src/ninline/__pycache__ tests/__pycache__

run:
	python3 -m ninline.cli --help
