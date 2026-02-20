.PHONY: fmt lint lint-fix typechk test test-htmlcov clean-up build update-lambda bak

help:
	@echo "Available targets:"
	@echo "  fmt              - Format the code using Ruff"
	@echo "  lint             - Check linting of the code using Ruff"
	@echo "  lint-fix         - Check and fix linting if the code using Ruff"
	@echo "  typechk          - Type check the code using mypy"
	@echo "  test             - Run unit tests"
	@echo "  test-htmlcov     - Run unit tests with html coverage report"
	@echo "  clean-up         - Clean up - remove htmlcov, __pycache__, pytest mypy and ruff cache dirs"
	@echo "  build            - Run the build script and create zip for lambda"
	@echo "  update-lambda    - Build and update lambda function code"
	@echo "  bak              - Backup S3 bucket into local bak directory"
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

clean-up:
	rm -rvf __pycache__ \
		.pytest_cache \
		.mypy_cache \
		.ruff_cache \
		.coverage \
		htmlcov \
		t212_to_digrin.zip \
		*.csv

build:
	rm -vf t212_to_digrin.zip
	zip -r t212_to_digrin.zip t212_to_digrin -x \*__pycache__ \*__main__.py

update-lambda:
	$(MAKE) build
	aws lambda update-function-code \
		--function-name t212-to-digrin \
		--zip-file fileb://t212_to_digrin.zip

bak:
	aws s3 sync s3://t212-to-digrin bak
