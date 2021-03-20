#!/bin/bash

set -e

PY3=3.9.2

HAS_PYENV=$(which pyenv >/dev/null 2>&1 && echo "true")
USE_PAMAC=$(which pamac >/dev/null 2>&1 && echo "true")
USE_APT_GET=$(which apt-get >/dev/null 2>&1 && echo "true")

git submodule update --init --recursive

docker ps

if [ -n $USE_PAMAC ]
then
    pamac install rofi \
                  thunar-volman \
                  nitrogen \
                  xcb-util-xrm \
                  xautolock \
                  kitty \
                  terminator \
                  brave \
                  xorg-xhost \
                  dunst
    pamac build picom-jonaburg-git
fi

if [ -n $USE_APT_GET ]
then
    sudo apt-get install libxcb-render0-dev \
                         libffi-dev \
                         libcairo2-dev \
                         libpangocairo-1.0-0 \
                         thunar \
                         rofi \
                         nitrogen \
                         xautolock \
                         terminator \
                         libx11-xcb-dev \
                         libxcb-render-util0-dev \
                         libxcb-damage0-dev \
                         libxcb-sync-dev \
                         libxcb-present-dev \
                         libdbus-1-dev \
                         uthash-dev \
                         libconfig-dev \
                         libgl-dev \
                         ninja-build \
                         meson
    git clone https://github.com/jonaburg/picom /tmp/picom
    cd /tmp/picom
    meson --buildtype=release . build
    ninja -C build
    # To install the binaries in /usr/local/bin (optional)
    sudo ninja -C build install
    cd -
fi

ln -s $(pwd)/rofi ~/.config

xdg-mime default Thunar.desktop inode/directory

pyenv virtualenv-delete -f qtile | true
pyenv virtualenv $PY3 qtile

$HOME/.pyenv/versions/qtile/bin/pip install --upgrade pip \
                                            jinja2 \
                                            cffi \
                                            xcffib \
                                            cairocffi

$HOME/.pyenv/versions/qtile/bin/pip install -r requirements.txt

rm -r ~/.config/qtile
ln -ns "$(pwd)" ~/.config/qtile

bash ~/.config/qtile/SpotifyController/install.sh

# Picom is a fork of compton but aliases itself to compton for
# backwards compatibility. Update all references to picom once
# all distros have been updated.
rm -r ~/.config/compton
rm -r ~/.config/picom
ln -ns "$(pwd)/picom" ~/.config/picom

if [ ! -f "/usr/share/xsessions/qtile.desktop" ]
then
    sudo cp $(pwd)/qtile.desktop /usr/share/xsessions/
fi

docker pull kyokley/vt

# Install i3lock-color
if [ -n $USE_PAMAC ]
then
    pamac install i3lock-color
fi

if [ -n $USE_APT_GET ]
then
    cur_dir="$(pwd)"
    git clone https://github.com/PandorasFox/i3lock-color.git /tmp/i3lock-color
    cd /tmp/i3lock-color
    git checkout $(git describe --tags --abbrev=0)
    sudo apt-get install -y libev-dev \
                            libxcb-composite0 \
                            libxcb-composite0-dev \
                            libxcb-xinerama0 \
                            libxcb-xinerama0-dev \
                            libxcb-xkb-dev \
                            libxcb-image0-dev \
                            libxcb-util-dev \
                            libxkbcommon-x11-dev \
                            libjpeg-turbo8-dev \
                            libpam0g-dev \
                            libxcb-randr0 \
                            libxcb-randr0-dev \
                            libxkbcommon-dev \
                            libxcb-xrm-dev \
                            autoconf
    autoreconf -i && ./configure && make && sudo make install
    cd "$cur_dir"
    rm -rf /tmp/i3lock-color
fi
xset dpms 600 600 600

python3 -m venv /tmp/gcal_env
/tmp/gcal_env/bin/pip install git+https://github.com/kyokley/gcalcli.git
/tmp/gcal_env/bin/gcalcli agenda
rm -rf /tmp/gcal_env

docker pull kyokley/gcalcli
