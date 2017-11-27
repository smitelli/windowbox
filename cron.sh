#!/usr/bin/env bash
set -e

SELF_DIR="$( cd $( dirname "${BASH_SOURCE[0]}" ) && pwd )"

source $SELF_DIR/src/.virtualenv/bin/activate

export WINDOWBOX_CONFIG_FILE=$SELF_DIR/src/windowbox/configs/production.cfg
python $SELF_DIR/src/fetch.py
