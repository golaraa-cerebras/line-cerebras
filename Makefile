.PHONY: install-dev format check test clean

# Install all dev dependencies
install-dev:
	pip install -e ".[dev,gemini,openai]"
	pre-commit install

# Run formatting and fix linting issues
format:
	pre-commit run --all-files

test:
	pytest -ra -v tests/ --cov=line --cov-report=term-missing
