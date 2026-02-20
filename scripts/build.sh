#!/usr/bin/env bash
set -e

# delete build dir if exists
[[ -d build ]] && rm -rvf build && echo "Deleting build dir." || echo "OK: build dir does not exist."
# create build dir
mkdir -v build

# # delete requirements if exists
# [[ -f requirements.txt ]] && rm requirements.txt && echo "Deleting requirements.txt file." || echo "OK: requirements.txt file does not exist."
# # export requirements
# uv export --format requirements-txt > requirements.txt
# # install pkgs into build dir
# uv pip install --requirements requirements.txt --target build

# copy source module into build dir
cp -r t212_to_digrin/* build/

# delete zip if exists
[[ -f lambda.zip ]] && rm lambda.zip && echo "Deleting lambda.zip file." || echo "OK: lambda.zip file does not exist."
# create new zip in a subshell
(cd build && zip -r ../lambda.zip . -x \*__pycache__)
