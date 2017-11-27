#!/usr/bin/env bash
set -e

SELF_DIR="$( cd $( dirname "${BASH_SOURCE[0]}" ) && pwd )"

cd "$SELF_DIR"

# Python components
rm -rf ./src/.virtualenv
virtualenv --always-copy ./src/.virtualenv
source ./src/.virtualenv/bin/activate
pip install --upgrade pip
pip install -r ./reqs.txt
deactivate

# JS/CSS components
# --no-save stops package-lock.json from being overwritten
npm install --prod --no-save
npm run-script build
rm -rf ./node_modules
