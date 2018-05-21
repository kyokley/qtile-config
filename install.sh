#!/bin/bash

set -e

sudo aptitude install libxcb-render0-dev libffi-dev libcairo2-dev libpangocairo-1.0-0

pyenv virtualenv 3.6.2 qtile

$HOME/.pyenv/versions/qtile/bin/pip install six
$HOME/.pyenv/versions/qtile/bin/pip install cffi
$HOME/.pyenv/versions/qtile/bin/pip install xcffib
$HOME/.pyenv/versions/qtile/bin/pip install cairocffi
$HOME/.pyenv/versions/qtile/bin/pip install qtile
$HOME/.pyenv/versions/qtile/bin/pip install -r requirements.txt

mkdir -p ~/.config/qtile
ln -s "$(pwd)/config.py" ~/.config/qtile/config.py
sudo ln -s $(pwd)/qtile.desktop /usr/share/xsessions/
