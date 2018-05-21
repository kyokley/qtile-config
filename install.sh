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
ln -s "$(pwd)/autostart.sh" ~/.config/qtile/autostart.sh
sudo ln -s $(pwd)/qtile.desktop /usr/share/xsessions/

pyenv virtualenv 3.6.2 vt_env
$HOME/.pyenv/versions/vt_env/bin/pip install git+https://github.com/kyokley/vittlify-cli.git

pyenv virtualenv 3.6.2 gcal_env
$HOME/.pyenv/versions/gcal_env/bin/pip install git+https://github.com/kyokley/gcalcli.git
