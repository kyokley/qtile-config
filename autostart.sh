#!/bin/bash

nitrogen --restore &
nm-applet &
xautolock -locker "$HOME/.pyenv/versions/qtile/bin/python $HOME/.config/qtile/pylocker.py" -time 10 -notify 10 -notifier "notify-send -t 5000 -i gtk-dialog-info 'Locking in 10 seconds'" -corners 0-00 &
xset dpms 600 600 600
