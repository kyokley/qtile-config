#!/bin/bash

set -e

PY3=3.8.2

docker ps

pamac install rofi \
              thunar-volman \
              nitrogen \
              xcb-util-xrm \
              xautolock \
              kitty \
              terminator \
              brave \
              picom

cp -r ./rofi ~/.config/rofi

xdg-mime default Thunar.desktop inode/directory

pyenv virtualenv-delete -f qtile | true
pyenv virtualenv $PY3 qtile

$HOME/.pyenv/versions/qtile/bin/pip install --upgrade pip \
                                            cffi \
                                            xcffib \
                                            cairocffi

$HOME/.pyenv/versions/qtile/bin/pip install -r requirements.txt

rm -r ~/.config/qtile
ln -ns "$(pwd)" ~/.config/qtile

# Picom is a fork of compton but aliases itself to compton for
# backwards compatibility. Update all references to picom once
# all distros have been updated.
rm -r ~/.config/compton
ln -ns "$(pwd)/compton" ~/.config/compton

if [ ! -h "/usr/share/xsessions/qtile.desktop" ]
then
    sudo ln -s $(pwd)/qtile.desktop /usr/share/xsessions/
fi

docker pull kyokley/vt

# Install i3lock-color
pamac install i3lock-color
xset dpms 600 600 600

python3 -m venv /tmp/gcal_env
/tmp/gcal_env/bin/pip install git+https://github.com/kyokley/gcalcli.git
/tmp/gcal_env/bin/gcalcli agenda
rm -rf /tmp/gcal_env

docker pull kyokley/gcalcli
