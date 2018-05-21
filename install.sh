#!/bin/bash

set -e

sudo aptitude install libxcb-render0-dev libffi-dev libcairo2-dev libpangocairo-1.0-0

pyenv virtualenv 3.6.2 qtile
pyenv activate qtile

pip install xcffib
pip install cairocffi
pip install qtile
pip install -r requirements.txt

mkdir -p ~/.config/qtile
ln -s "$(pwd)/config.py" ~/.config/qtile/config.py
sudo cp $(pwd)/qtile.desktop /usr/share/xsessions/
