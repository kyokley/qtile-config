#!/bin/bash

set -e

PY3=3.6.7

docker ps

pamac install rofi \
              thunar-volman \
              nitrogen \
              xcb-util-xrm \
              xautolock \
              kitty \
              picom

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

if [ ! -h "~/.config/qtile" ]
then
    ln -s "$(pwd)" ~/.config/qtile
fi

if [ ! -h "~/.config/picom" ]
then
    ln -s "$(pwd)/picom" ~/.config/picom
fi

if [ ! -h "/usr/share/xsessions/qtile.desktop" ]
then
    sudo ln -s $(pwd)/qtile.desktop /usr/share/xsessions/
fi

docker pull kyokley/vt

# Install i3lock-color
pamac build i3lock-color
xset dpms 600 600 600

virtualenv -p python3 /tmp/gcal_env
/tmp/gcal_env/bin/pip install git+https://github.com/kyokley/gcalcli.git
/tmp/gcal_env/bin/gcalcli agenda
rm -rf /tmp/gcal_env

docker pull kyokley/gcalcli
