.PHONY: fmt lint lint-fix typechk test test-htmlcov

help:
	@echo "Available targets:"
	@echo "  fmt              - Format the code using Ruff"
	@echo "  lint             - Check linting of the code using Ruff"
	@echo "  lint-fix         - Check and fix linting if the code using Ruff"
	@echo "  typechk          - Type check the code using mypy"
	@echo "  test             - Run unit tests"
	@echo "  test-htmlcov        - Run unit tests with html coverage report"
	@echo "  help             - Show this help message"

fmt:
	uv run --dev ruff format

lint:
	uv run --dev ruff check

lint-fix:
	uv run --dev ruff check --fix

typechk:
	uv run --dev mypy .

test:
	uv run --dev pytest tests/ 

test-htmlcov:
	uv run --dev pytest tests/ --cov-report=html:htmlcov
