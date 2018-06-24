#!/bin/bash

nitrogen --restore &
nm-applet &

# NOTE: The minimum killtime below is 10 minutes
xautolock -locker "$HOME/.pyenv/versions/qtile/bin/python $HOME/.config/qtile/pylocker.py" -time 10 -notify 10 -notifier "notify-send -t 5000 -i gtk-dialog-info 'Locking in 10 seconds'" -corners 0-00 -killer "xset dpms force off" -killtime 10 &
