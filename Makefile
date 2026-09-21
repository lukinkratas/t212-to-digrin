.PHONY: fmt fmtchk lint lintchk typechk clean-up bak

help:
	@echo "Available targets:"
	@echo "  fmt              - Format the code using Ruff and Terraform"
	@echo "  fmtchk           - Check formatting using Ruff and Terraform"
	@echo "  lint             - Lint the code using Ruff and sqlfluff"
	@echo "  lintchk          - Check linting using Ruff and sqlfluff"
	@echo "  typechk          - Type check the code using mypy"
	@echo "  clean-up         - Clean up - remove htmlcov, __pycache__, pytest mypy and ruff cache dirs"
	@echo "  bak              - Backup S3 bucket into local bak directory"
	@echo "  help             - Show this help message"

fmt:
	uv run --dev ruff format
	terraform fmt terraform/

fmtchk:
	uv run --dev ruff format --check
	terraform fmt -check terraform/

lint:
	uv run --dev ruff check --fix

lintchk:
	uv run --dev ruff check

typechk:
	uv run --dev mypy .

clean-up:
	rm -rvf __pycache__ \
		.pytest_cache \
		.mypy_cache \
		.ruff_cache \
		*.csv

bak:
	aws s3 sync s3://t212-to-digrin bak
