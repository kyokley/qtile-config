#!/bin/bash

set -e

$HOME/.pyenv/versions/qtile/bin/python $HOME/.config/qtile/pylocker.py
xset dpms force off
