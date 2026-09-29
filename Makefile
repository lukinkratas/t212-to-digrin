.PHONY: fmt fmtchk lint lintchk typechk clean-up deploy

help:
	@echo "Available targets:"
	@echo "  fmt              - Format the code using Ruff and Terraform"
	@echo "  fmtchk           - Check formatting using Ruff and Terraform"
	@echo "  lint             - Lint the code using Ruff and sqlfluff"
	@echo "  lintchk          - Check linting using Ruff and sqlfluff"
	@echo "  typechk          - Type check the code using mypy"
	@echo "  clean-up         - Clean up - remove htmlcov, __pycache__, pytest mypy and ruff cache dirs"
	@echo "  deploy           - deploy infra based on terraform config"
	@echo "  help             - Show this help message"

fmt:
	uv run --dev ruff format
	terraform fmt infra/

fmtchk:
	uv run --dev ruff format --check
	terraform fmt -check infra/

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
		*.csv \
		exports/*

deploy:
	(cd infra && terraform validate && terraform plan && terraform apply)
