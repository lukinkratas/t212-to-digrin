#!/usr/bin/env bash
set -e

# delete build dir if exists
[[ -d build ]] && rm -rvf build && echo "Deleting build dir." || echo "OK: build dir does not exist."
# create build dir
mkdir -v build
# install pkgs into build dir
python3 -m pip install pyproject.toml --target build
# copy source module into build dir
cp -r t212_to_digrin build/

# delete zip if exists
[[ -f lambda.zip ]] && rm lambda.zip && echo "Deleting zip file." || echo "OK: zip file does not exist."
# create new zip in a subshell
(cd build && zip -r ../lambda.zip . -x \*__pycache__)
