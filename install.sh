#!/bin/bash

set -e

PY3=3.6.7

docker ps

pamac install rofi \
              thunar-volman \
              nitrogen \
              xcb-util-xrm \
              xautolock

cp -r ./rofi ~/.config/rofi

xdg-mime default Thunar.desktop inode/directory

pyenv virtualenv $PY3 qtile

$HOME/.pyenv/versions/qtile/bin/pip install --upgrade pip \
                                            cffi \
                                            xcffib \
                                            cairocffi

$HOME/.pyenv/versions/qtile/bin/pip install six \
                                            qtile \
                                            -r requirements.txt

ln -s "$(pwd)" ~/.config/qtile

sudo ln -s $(pwd)/qtile.desktop /usr/share/xsessions/

docker pull kyokley/vt

# Install i3lock-color
pamac build i3lock-color
xset dpms 600 600 600

virtualenv -p python3 /tmp/gcal_env
/tmp/gcal_env/bin/pip install git+https://github.com/kyokley/gcalcli.git
/tmp/gcal_env/bin/gcalcli agenda
rm -rf /tmp/gcal_env

docker pull kyokley/gcalcli
