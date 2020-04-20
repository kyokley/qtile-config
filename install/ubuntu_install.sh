#!/bin/bash

PY3=3.8.2

sudo aptitude install libxcb-render0-dev \
                      libffi-dev \
                      libcairo2-dev \
                      libpangocairo-1.0-0 \
                      thunar \
                      rofi \
                      nitrogen \
                      xautolock \
                      compton

cp -r ./rofi ~/.config/rofi

xdg-mime default Thunar.desktop inode/directory

pyenv install $PY3

pyenv virtualenv-delete qtile
pyenv virtualenv $PY3 qtile

$HOME/.pyenv/versions/qtile/bin/pip install --upgrade pip \
                                            cffi \
                                            xcffib \
                                            cairocffi

$HOME/.pyenv/versions/qtile/bin/pip install -r requirements.txt

ln -ns "$(pwd)" ~/.config/qtile

ln -ns "$(pwd)/compton" ~/.config/compton

if [ ! -a "/usr/share/xsessions/qtile.desktop" ]
then
    sudo ln -s $(pwd)/qtile.desktop /usr/share/xsessions/
fi

docker pull kyokley/vt

# Install i3lock-color
cur_dir="$(pwd)"
git clone https://github.com/PandorasFox/i3lock-color.git /tmp/i3lock-color
cd /tmp/i3lock-color
git checkout $(git describe --tags --abbrev=0)
sudo aptitude install -y libev-dev \
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
xset dpms 600 600 600

python3 -m venv /tmp/gcal_env
/tmp/gcal_env/bin/pip install git+https://github.com/kyokley/gcalcli.git
/tmp/gcal_env/bin/gcalcli agenda
rm -rf /tmp/gcal_env

docker pull kyokley/gcalcli
