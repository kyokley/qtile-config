#!/bin/bash

set -e

PY27=2.7.13
PY3=3.6.2

sudo aptitude install libxcb-render0-dev \
                      libffi-dev \
                      libcairo2-dev \
                      libpangocairo-1.0-0 \
                      thunar \
                      dmenu \
                      nitrogen

xdg-mime default Thunar.desktop inode/directory

pyenv virtualenv $PY3 qtile

$HOME/.pyenv/versions/qtile/bin/pip install six \
                                            cffi \
                                            xcffib \
                                            cairocffi \
                                            qtile \
                                            -r requirements.txt

ln -s "$(pwd)" ~/.config/qtile

sudo ln -s $(pwd)/qtile.desktop /usr/share/xsessions/

pyenv virtualenv $PY3 vt_env
$HOME/.pyenv/versions/vt_env/bin/pip install git+https://github.com/kyokley/vittlify-cli.git

pyenv virtualenv $PY27 gcal_env
$HOME/.pyenv/versions/gcal_env/bin/pip install git+https://github.com/kyokley/gcalcli.git

# Install i3lock-color
cur_dir="$(pwd)"
git clone https://github.com/PandorasFox/i3lock-color.git /tmp/i3lock-color
cd /tmp/i3lock-color
sudo aptitude install -y libev-dev \
                         libxcb-composite0 \
                         libxcb-composite0-dev \
                         libxcb-xinerama0 \
                         libxcb-randr0 \
                         libxcb-xinerama0-dev \
                         libxcb-xkb-dev \
                         libxcb-image0-dev \
                         libxcb-util-dev \
                         libxkbcommon-x11-dev \
                         libjpeg-turbo8-dev \
                         libpam0g-dev \
                         libxcb-randr0-dev \
                         libxkbcommon-dev \
                         autoconf
autoreconf -i && ./configure && make && sudo make install
cd "$cur_dir"
rm -rf /tmp/i3lock-color
xset dpms 600 600 600
