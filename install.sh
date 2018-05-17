#!/bin/bash

sudo aptitude install libxcb-render0-dev libffi-dev libcairo2-dev libpangocairo-1.0-0
sudo pip3 install xcffib
sudo pip3 install cairocffi
sudo pip3 install qtile

sudo cp qtile.desktop /usr/share/xsessions/
